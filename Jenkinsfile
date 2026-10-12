pipeline {
    agent any

    environment {
        IMAGE_REPO = 'tanweerkhan/myapp'
        CONTAINER_NAME = 'myapp'
        APP_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Application') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    python -m unittest test_app.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_REPO}:${BUILD_NUMBER} \
                      -t ${IMAGE_REPO}:latest .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DOCKERHUB_TOKEN" |
                          docker login -u "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        docker push ${IMAGE_REPO}:${BUILD_NUMBER}
                        docker push ${IMAGE_REPO}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                      --restart unless-stopped \
                      --name ${CONTAINER_NAME} \
                      -p ${APP_PORT}:5000 \
                      ${IMAGE_REPO}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    for i in $(seq 1 15); do
                      if curl -fsS http://localhost:${APP_PORT}/health; then
                        echo "Deployment successful"
                        exit 0
                      fi
                      sleep 2
                    done

                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }
}
