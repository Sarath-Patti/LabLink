pipeline {
    agent any

    environment {
        LABLINK_ENVIRONMENT = 'CI'
        LABLINK_DB_HOST = 'localhost'
        LABLINK_DB_PORT = '5432'
        LABLINK_DB_NAME = 'lablink_dev'
        LABLINK_DB_USER = 'sarathpatti'
        LABLINK_DB_PASSWORD = ''
        LABLINK_API_PORT = '5099'
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                echo '=== Stage 1: Checkout Source Code ==='
                checkout scm
            }
        }

        stage('Environment Validation') {
            steps {
                echo '=== Stage 2: Validating Environment Dependencies ==='
                sh 'python3 --version'
                sh 'dotnet --version'
                sh 'bash --version'
                sh 'docker compose version || docker --version'
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo '=== Stage 3: Setup Virtual Environment ==='
                sh './scripts/setup_python.sh'
            }
        }

        stage('Python Quality') {
            steps {
                echo '=== Stage 4: Python Static Quality Checks ==='
                sh './scripts/run_python_quality.sh'
            }
        }

        stage('Python Tests') {
            steps {
                echo '=== Stage 5: Python Pytest Suite ==='
                sh './scripts/run_python_tests.sh'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'python_test_results.xml'
                }
            }
        }

        stage('.NET Quality & Tests') {
            steps {
                echo '=== Stage 6: .NET Build, Format & xUnit Tests ==='
                sh './scripts/run_dotnet_tests.sh'
            }
        }

        stage('Docker Compose Validation & Build') {
            steps {
                echo '=== Stage 7: Docker Compose Config & Image Build ==='
                sh 'docker compose -f docker/docker-compose.yml config'
                sh 'docker compose -f docker/docker-compose.yml build'
            }
        }

        stage('PostgreSQL Service') {
            steps {
                echo '=== Stage 8: PostgreSQL Service Startup & Readiness ==='
                sh './scripts/start_postgres.sh'
                sh './scripts/wait_for_postgres.sh'
                sh './scripts/migrate_database.sh'
            }
        }

        stage('API Service & Smoke Test') {
            steps {
                echo '=== Stage 9: API Service Startup & Integration Smoke Test ==='
                sh './scripts/start_api.sh'
                sh './scripts/run_integration_tests.sh'
            }
        }

        stage('Packaging & Artifacts') {
            steps {
                echo '=== Stage 10: Archiving Test Artifacts and Logs ==='
                archiveArtifacts artifacts: 'python_test_results.xml, api_ci.log', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo '=== Executing Post-Pipeline Cleanup ==='
            sh './scripts/cleanup.sh'
        }
        success {
            echo '=== LabLink CI/CD Pipeline Succeeded! ==='
        }
        failure {
            echo '=== LabLink CI/CD Pipeline Failed! ==='
        }
    }
}
