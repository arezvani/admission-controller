from flask import Flask, request, jsonify

app = Flask(__name__)
 
#POST route for Admission Controller  
@app.route('/validate', methods=['POST'])

#Admission Control Logic
def deployment_webhook():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")
    try:
        if request_info["request"]["object"]["metadata"]["labels"].get("manage_by"):
            #Send response back to controller if validations succeeds
            if request_info["request"]["object"]["metadata"]["labels"]["manage_by"] == 'abriment':
                return k8s_response(True, uid, "manage_by label exists")
            else:
                return k8s_response(False, uid, "Wrong value for manage_by label")
    except:
        return k8s_response(False, uid, "No labels exist. A manage_by label is required")
    
    #Send response back to controller if failed
    return k8s_response(False, uid, "Not allowed without a manage_by label")

#Function to respond back to the Admission Controller
def k8s_response(allowed, uid, message):
     return jsonify({"apiVersion": "admission.k8s.io/v1", "kind": "AdmissionReview", "response": {"allowed": allowed, "uid": uid, "status": {"message": message}}})

if __name__ == '__main__':
    app.run(ssl_context=('certs/webhook.crt', 'certs/webhook.key'), debug=True, host='0.0.0.0', port=443)