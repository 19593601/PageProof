from flask import Flask, render_template, request
import CoolProp.CoolProp as cp

app = Flask(__name__)

def convert_units(value, original_unit, target_unit):
    original_unit = original_unit.lower()
    target_unit = target_unit.lower()
    if original_unit == target_unit:
        return value
    if original_unit in ['kpa', 'mpa', 'psi', 'bar', 'kg/cm²', 'mmhg']:
        if original_unit == 'kpa':
            value = value
        elif original_unit == 'mpa':
            value = value * 1000
        elif original_unit == 'psi':
            value = value / 0.1450377377
        elif original_unit == 'bar':
            value = value * 100
        elif original_unit == 'kg/cm²':
            value = value / 10.19716213
        elif original_unit == 'mmhg':
            value = value / 7.500615613

        if target_unit == 'kpa':
            return value
        elif target_unit == 'mpa':
            return value / 1000
        elif target_unit == 'psi':
            return value * 6.89476
        elif target_unit == 'bar':
            return value / 100
        elif target_unit == 'kg/cm²':
            return value * 98.0665
        elif target_unit == 'mmhg':
            return value * 7.50062
    elif original_unit in ['c', 'f', 'k']:
        if original_unit == 'c':
            value = value
        elif original_unit == 'f':
            value = (value - 32) * 5 / 9
        elif original_unit == 'k':
            value = value - 273.15

        if target_unit == 'c':
            return value
        elif target_unit == 'f':
            return (value * 9 / 5) + 32
        elif target_unit == 'k':
            return value + 273.15
    return None

def calculate_properties(temp, pressure, temp_unit, pressure_unit):
    temp_k = convert_units(temp, temp_unit, 'C') + 273.15
    pressure_pa = convert_units(pressure, pressure_unit, 'kPa') * 1000  # Convert from kPa to Pa

    density, enthalpy, specific_heat = cp.PropsSI(['D', 'H', 'C'], 'T', temp_k, 'P', pressure_pa, 'Water')
    viscosity = cp.PropsSI('V', 'T', temp_k, 'P', pressure_pa, 'Water')  # Calculate viscosity

    return {
        "temp": round(convert_units(temp_k - 273.15, 'C', temp_unit), 4),
        "v": round(1 / density, 4),  # Specific volume is the inverse of density
        "h": round(enthalpy / 1000, 4),    # Convert from J/kg to kJ/kg
        "Specific Heat": round(specific_heat / 1000, 4),    # Convert from J/kg·K to kJ/kg·K
        "viscosity": round(viscosity * 1000, 4),  # Add viscosity
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    properties = None
    temp_unit = None
    error = None

    if request.method == 'POST':
        temp_unit = request.form.get('temp_unit')
        temperature_str = request.form.get('temperature')
        pressure_unit = request.form.get('pressure_unit')
        pressure_str = request.form.get('pressure')

        if temperature_str and pressure_str:  # Check if the fields are not empty
            temperature = float(temperature_str)
            pressure = float(pressure_str)
        
            properties = calculate_properties(temperature, pressure, temp_unit, pressure_unit)
        else:
            error = "Please fill in all fields."

    return render_template('index.html', properties=properties, temp_unit=temp_unit, error=error)

if __name__ == "__main__":
    app.run(debug=True)
