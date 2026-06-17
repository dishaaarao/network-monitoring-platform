pipeline {
    agent any

    environment {
        IMAGE_NAME = 'network-monitoring-app'
        IMAGE_TAG = "${BUILD_NUMBER}"
        REGISTRY = "${env.DOCKER_REGISTRY ?: 'docker.io/your-dockerhub-username'}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest'
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m pip install -r requirements.txt
                    python3 -c 'from app import app; c = app.test_client(); assert c.get("/health").status_code == 200; assert c.get("/api/devices").status_code == 200; print("unit tests passed")'


                    docker rm -f test-app || true
                    docker run -d --name test-app --network container:$HOSTNAME ${IMAGE_NAME}:${IMAGE_TAG}
                    sleep 5
                    curl -f http://localhost:8000/health
                    curl -f http://localhost:8000/api/status
                    curl -f http://localhost:8000/metrics
                    docker stop test-app
                    docker rm test-app
                '''
            }
        }

        stage('Push') {
            when {
                branch 'main'
            }
            steps {
                echo 'Configure Jenkins credential ID docker-registry-credentials to enable registry push.'
                echo 'Then uncomment push commands in Jenkinsfile.'
                // withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                //     sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                //     sh 'docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                // }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                sh 'kubectl apply -f k8s/namespace.yaml'
                sh 'kubectl apply -f k8s/configmap.yaml'
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl apply -f k8s/hpa.yaml'
                sh 'kubectl apply -f k8s/ingress.yaml'
                sh 'kubectl apply -f k8s/monitoring/'
                sh 'kubectl rollout status deployment/network-monitoring-app -n network-monitoring'
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
    }
}
