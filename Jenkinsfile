pipeline {
    agent any
    stages {
        stage("Code") {
            steps {
                git url: "https://github.com/Sidgore799/dispatch-automation.git", branch: "master"
            }
        }
        stage("Build") {
            steps {
                sh "docker build -t dispatch-app ."
            }
        }
        stage("Test") {
            steps {
                sh "docker compose run --rm --no-deps dispatch-app python -c 'import app; print(\"app imports fine\")'"
            }
        }
        stage("Deploy") {
            steps {
                sh "docker compose up -d"
                sh "sleep 5 && curl -sf http://localhost:5000/login > /dev/null"
            }
        }
    }
}
