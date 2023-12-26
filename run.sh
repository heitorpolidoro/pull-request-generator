smee -u https://smee.io/github_app_tests -p 5000 -P / &

PRIVATE_KEY=$(cat private-key.pem) flask run --debug
export BUILDPULSE_ACCESS_KEY_ID=<your_access_key_id>
PRIVATE_KEY=$(cat private-key.pem) flask run --debug

