import os
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import GlucoseRecord
import joblib

# === Load trained model using joblib ===
def load_model(model_name):
    model_path = os.path.join(settings.BASE_DIR, 'users', 'ml_models', f"{model_name.lower()}_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to load {model_name} model: {e}")

# === Dashboard view (user + admin) ===
@login_required
def dashboard(request):
    error = None
    forecasted_values = []
    horizons = [5, 15, 30, 60, 480, 720, 1440]  # minutes
    selected_model = None

    if request.method == "POST":
        try:
            # Get input data from form
            temp = float(request.POST.get('temperature', 36.0))
            hr = float(request.POST.get('heart_rate', 70))
            ibi = float(request.POST.get('interbeat_interval', 0.85))
            model_choice = request.POST.get('model_choice', 'ARIMA')
            selected_model = model_choice

            # Load model
            model = load_model(model_choice)

            # Forecast depending on model type
            if model_choice.upper() == "ARIMA":
                # Only past glucose values
                prev = GlucoseRecord.objects.filter(user=request.user).order_by('-recorded_at')[:10]
                series = np.array([r.predicted_glucose for r in reversed(prev) if r.predicted_glucose is not None])
                if len(series) > 0:
                    forecasted_values = model.forecast(steps=len(horizons), y=series).tolist()
                else:
                    forecasted_values = [100.0] * len(horizons)

            elif model_choice.upper() == "SARIMAX":
                # Use exogenous variables
                exog = pd.DataFrame({
                    "HeartRate": [hr]*len(horizons),
                    "IBI": [ibi]*len(horizons),
                    "Temperature": [temp]*len(horizons)
                })[["HeartRate", "IBI", "Temperature"]]
                forecast = model.get_forecast(steps=len(horizons), exog=exog)
                forecasted_values = forecast.predicted_mean.tolist()

            # Save latest predicted glucose
            if forecasted_values:
                GlucoseRecord.objects.create(
                    user=request.user,
                    temperature=temp,
                    heart_rate=hr,
                    interbeat_interval=ibi,
                    chosen_model=model_choice,
                    predicted_glucose=forecasted_values[0]
                )

        except FileNotFoundError as fnf:
            error = str(fnf)
        except RuntimeError as rte:
            error = str(rte)
        except Exception as e:
            error = f"Unknown error occurred: {e}"

    # Past records
    past_records = GlucoseRecord.objects.filter(user=request.user).order_by('-recorded_at')[:20]

    context = {
        "forecasted_values": forecasted_values,
        "horizons": horizons,
        "past_records": past_records,
        "error": error,
        "selected_model": selected_model
    }

    # Admin dashboard
    if request.user.is_superuser:
        users = User.objects.all()
        records = GlucoseRecord.objects.select_related('user').order_by('-recorded_at')
        context.update({"users": users, "records": records})
        return render(request, "users/admin_dashboard.html", context)

    # User dashboard
    return render(request, "users/user_dashboard.html", context)

# === Admin: create user ===
@login_required
def create_user(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, "users/create_user.html", {"form": form})
