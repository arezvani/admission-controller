from flask import Flask, request, jsonify
import jsonpatch
import base64

app = Flask(__name__)
 
#POST route for Admission Controller  
@app.route('/mutate', methods=['POST'])

#Admission Control Logic
def deployment_webhook():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")

    for i, container in enumerate(request_info["request"]["object"]["spec"]["template"]["spec"]["containers"]):
        image = request_info["request"]["object"]["spec"]["template"]["spec"]["containers"][i]["image"]
        if not request_info["request"]["object"]["spec"]["template"]["spec"]["containers"][i]["image"].startswith('docker.io'):
            json_patch = jsonpatch.JsonPatch([{"op": "replace", "path": f"/spec/template/spec/containers/{i}/image", "value": f"docker.io/{image}"}])
            return k8s_response(True, uid, "Change Image", json_patch)

#Function to respond back to the Admission Controller
def k8s_response(allowed, uid, message, json_patch):
    base64_patch = base64.b64encode(json_patch.to_string().encode("utf-8")).decode("utf-8")
    return jsonify({"apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": True,
            "patchType": "JSONPatch",
            "status": {"message": message},
            "patch": json_patch,
        },
    })

if __name__ == '__main__':
    app.run(ssl_context=('certs/webhook.crt', 'certs/webhook.key'), debug=True, host='0.0.0.0', port=443)