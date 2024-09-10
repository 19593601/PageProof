from flask import Flask, render_template, request
import CoolProp.CoolProp as cp

app = Flask(__name__)

def convert_units(value, original_unit, target_unit):
    if original_unit == 'F' and target_unit == 'C':
        return (value - 32) * 5.0/9.0
    elif original_unit == 'C' and target_unit == 'K':
        
        
        return value + 273.15
    elif original_unit == 'F' and target_unit == 'K':
        return (value - 32) * 5.0/9.0 + 273.15
    else:
        return value

def calculate_properties(temp, temp_unit):
    temp_k = convert_units(temp, temp_unit, 'K')
    if temp_k < 273.06 or temp_k > 647.096:
        return {"error": "Temperature must be between 273.06 K and 647.096 K."}

    pressure_pa = cp.PropsSI('P', 'T', temp_k, 'Q', 1, 'Water')  # Calculate saturation pressure at given temperature
    enthalpy_vapor = cp.PropsSI('H', 'T', temp_k, 'Q', 1, 'Water')  # Calculate enthalpy of saturated vapor
    enthalpy_water = cp.PropsSI('H', 'T', temp_k, 'Q', 0, 'Water')  # Calculate enthalpy of saturated water
    density_vapor = cp.PropsSI('D', 'T', temp_k, 'Q', 1, 'Water')  # Calculate density of saturated vapor
    density_water = cp.PropsSI('D', 'T', temp_k, 'Q', 0, 'Water')  # Calculate density of saturated water

    return {
        "temp": round(temp_k, 4),
        "Vapor_Pressure": round(pressure_pa / 1e6, 4),  # Convert from Pa to MPa
        "Latent_Heat_Vapor": round((enthalpy_vapor - enthalpy_water) / 1000, 4),  # Convert from J/kg to kJ/kg
        "Specific_Enthalpy_Saturated_Vapor": round(enthalpy_vapor / 1000, 4),  # Convert from J/kg to kJ/kg
        "Specific_Enthalpy_Saturated_Water": round(enthalpy_water / 1000, 4),  # Convert from J/kg to kJ/kg
        "Specific_Volume_Saturated_Vapor": round(1 / density_vapor, 4),  # Specific volume is the inverse of density
        "Specific_Volume_Saturated_Water": round(1 / density_water, 4),  # Specific volume is the inverse of density
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    properties = None
    temp_unit = None
    error = None

    if request.method == 'POST':
        temp_unit = request.form.get('temp_unit')
        temperature_str = request.form.get('temperature')

        if temperature_str:  # Check if the field is not empty
            temperature = float(temperature_str)
            properties = calculate_properties(temperature, temp_unit)
            if "error" in properties:
                error = properties["error"]
                properties = None
        else:
            error = "Please fill in all fields."

    return render_template('index.html', properties=properties, temp_unit=temp_unit, error=error)

if __name__ == "__main__":
    app.run(debug=True)
