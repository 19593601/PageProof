from flask import Flask, request, render_template
import CoolProp.CoolProp as cp

app = Flask(__name__)

def convert_units(value, original_unit, target_unit):
    conversion_factors = {
        'kPa abs': 1e3, 'MPa abs': 1e6, 'psi abs': 6894.76, 'bar abs': 1e5, 'kg/cm2 abs': 98066.5, 'mmHg abs': 133.322,
        'kPaG': 1e3, 'MPaG': 1e6, 'psig': 6894.76, 'barG': 1e5, 'kg/cm2G': 98066.5, 'mmHgG': 133.322
    }
    return value * conversion_factors.get(original_unit, 1)

def calculate_properties(pressure, pressure_unit):
    valid_units = ['Pa', 'kPa', 'MPa', 'bar', 'atm']
    if pressure_unit not in valid_units:
        return {"error": "Invalid pressure unit. Please select a valid unit."}

    try:
        pressure_pa = convert_units(pressure, pressure_unit, 'Pa')
        if pressure_pa < 611.657 or pressure_pa > 22.064e6:
            return {"error": "Pressure must be between 611.657 Pa and 22.064 MPa."}

        temp_k = cp.PropsSI('T', 'P', pressure_pa, 'Q', 1, 'Water')  # Calculate saturation temperature at given pressure
        enthalpy_vapor = cp.PropsSI('H', 'P', pressure_pa, 'Q', 1, 'Water')  # Calculate enthalpy of saturated vapor
        enthalpy_water = cp.PropsSI('H', 'P', pressure_pa, 'Q', 0, 'Water')  # Calculate enthalpy of saturated water
        density_vapor = cp.PropsSI('D', 'P', pressure_pa, 'Q', 1, 'Water')  # Calculate density of saturated vapor
        density_water = cp.PropsSI('D', 'P', pressure_pa, 'Q', 0, 'Water')  # Calculate density of saturated water

        return {
            "temperature": round(temp_k - 273.15, 4),  # Convert from K to °C
            "Latent_Heat_Vapor": round((enthalpy_vapor - enthalpy_water) / 1000, 4),  # Convert from J/kg to kJ/kg
            "Specific_Enthalpy_Saturated_Vapor": round(enthalpy_vapor / 1000, 4),  # Convert from J/kg to kJ/kg
            "Specific_Enthalpy_Saturated_Water": round(enthalpy_water / 1000, 4),  # Convert from J/kg to kJ/kg
            "Specific_Volume_Saturated_Vapor": round(1 / density_vapor, 4),  # Specific volume is the inverse of density
            "Specific_Volume_Saturated_Water": round(1 / density_water, 4),  # Specific volume is the inverse of density
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    properties = None
    pressure_unit = None
    error = None

    if request.method == 'POST':
        pressure_unit = request.form.get('pressure_unit')
        pressure_str = request.form.get('pressure')

        if pressure_str and pressure_unit:  # Check if both fields are not empty
            if pressure_unit not in ['Pa', 'kPa', 'MPa', 'bar', 'atm']:  # Check if pressure_unit is valid
                error = "Invalid pressure unit. Please select a valid unit."
            else:
                try:
                    pressure = float(pressure_str)
                    properties = calculate_properties(pressure, pressure_unit)
                    if "error" in properties:
                        error = properties["error"]
                        properties = None
                except ValueError:
                    error = "Invalid pressure value. Please enter a valid number."
        else:
            error = "Please fill in all fields."

    return render_template('index.html', properties=properties, pressure_unit=pressure_unit, error=error)

if __name__ == "__main__":
    app.run(debug=True)
