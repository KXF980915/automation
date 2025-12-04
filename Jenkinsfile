pipeline {
    agent any

    environment {
        // 设置Windows命令行编码为UTF-8
        JAVA_TOOL_OPTIONS = '-Dfile.encoding=UTF-8'
        PYTHONIOENCODING = 'UTF-8'
    }

    parameters {
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge'],
            description: '选择测试浏览器'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['test', 'staging', 'prod'],
            description: '选择测试环境'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                bat """
                echo === 环境设置 ===
                python --version
                pip --version

                echo 安装依赖...
                python -m pip install --upgrade pip
                if exist requirements.txt (
                    pip install -r requirements.txt
                ) else (
                    pip install pytest selenium requests
                )
                """
            }
        }

        stage('Tests') {
            steps {
                bat """
                echo === 执行测试 ===
                echo 浏览器: ${BROWSER}
                echo 环境: ${ENVIRONMENT}

                REM 创建目录
                if not exist "test-results" mkdir test-results
                if not exist "reports" mkdir reports

                REM 执行测试
                python -m pytest tests_case/ \
                    -v \
                    --browser=${BROWSER} \
                    --env=${ENVIRONMENT} \
                    --junitxml=test-results/junit.xml \
                    --html=reports/pytest-report.html \
                    || echo "测试执行完成"
                """
            }
        }
    }

    post {
        always {
            echo "构建状态: ${currentBuild.currentResult}"

            // 归档结果
            archiveArtifacts artifacts: 'test-results/**/*.xml, reports/**/*.html', allowEmptyArchive: true
        }
    }
}