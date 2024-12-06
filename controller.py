from flask import Flask, Response, render_template
import traci
import time
import threading

app = Flask(__name__)

simulating = False

def run_sumo():
    global simulating
    sumo_binary = "sumo"  
    config_file = "sumo_test/simulation.sumocfg"

    traci.start([sumo_binary, "-c", config_file])
    simulating = True

    while simulating:
        traci.simulationStep()  
        time.sleep(0.1)  

    traci.close()

def get_simulation_data():
    while simulating:
        vehicles = traci.vehicle.getIDList()
        data = []
        for vehicle_id in vehicles:
            position = traci.vehicle.getPosition(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)
            data.append({"id": vehicle_id, "position": position, "speed": speed})
        yield f"data: {data}\n\n"  
        time.sleep(0.1)

@app.route('/start_simulation')
def start_simulation():
    global simulating
    if not simulating:
        threading.Thread(target=run_sumo).start()
    return "Simulation started"

@app.route('/stop_simulation')
def stop_simulation():
    global simulating
    simulating = False
    return "Simulation stopped"

@app.route('/stream')
def stream():
    return Response(get_simulation_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
