pipeline {
    agent any
    stages {
        stage("Code") {
            steps {
                // Works when the job is "Pipeline script from SCM". For a plain pipeline job use:
                // git url: "https://github.com/<username>/<repo>.git", branch: "main"
                checkout scm
            }
        }
        stage("Build") {
            steps {
                sh "docker compose build"
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
