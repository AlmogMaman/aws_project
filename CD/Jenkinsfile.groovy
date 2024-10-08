pipeline {
    agent any

    parameters {
        string(name: 'SERVICE_NAME', defaultValue: '', description: 'The name of the service being deployed')
        string(name: 'VERSION', defaultValue: '', description: 'The new version of the image')
        string(name: 'REPO_URI', defaultValue: '', description: 'The ECR repository URI')
    }

    stages {
        stage('Deploy') {
            steps {
                script {
                    def serviceName = params.SERVICE_NAME
                    def imageRepo = params.REPO_URI
                    def newVersion = params.VERSION

                    echo "Deploying ${serviceName} with image version ${newVersion} from ${imageRepo}"

                    sh """
                        aws cloudformation update-stack \
                        --template-url https://s3.amazonaws.com/almog-maman-cloudformation-files/main.yaml \
                        --stack-name main \
                        --parameters ParameterKey=ImageUri,ParameterValue=${imageRepo}:${newVersion} \
                        --capabilities CAPABILITY_IAM
                    """
                }
            }
        }
    }
}
