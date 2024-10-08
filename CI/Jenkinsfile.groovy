pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    def serviceName = env.SERVICE_NAME
                    sh "docker build -t myuser/${serviceName}:latest ${serviceName}/."
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def serviceName = env.SERVICE_NAME
                    sh "docker run --rm myuser/${serviceName}:latest python -m unittest discover -s ${serviceName}/tests"
                }
            }
        }
        stage('Push to ECR') {
            steps {
                script {
                    def serviceName = env.SERVICE_NAME
                    sh "docker tag myuser/${serviceName}:latest ${env.REPO_URI}:${VERSION}"
                    sh "docker push ${env.REPO_URI}:latest"
                }
            }
        }
        stage('Trigger CD Pipeline') {
            steps {
                script {
                    def serviceName = env.SERVICE_NAME
                    def version = getNextVersion() // Function to get the next version number
                    
                    build job: 'CD-Pipeline', parameters: [
                        string(name: 'SERVICE_NAME', value: serviceName),
                        string(name: 'VERSION', value: version),
                        string(name: 'REPO_URI', value: env.REPO_URI)
                    ]
                }
            }
        }
    }
}


def getNextVersion() {
    // Logic to fetch the current version from ECR and increment it
    return '1' // Placeholder
}
