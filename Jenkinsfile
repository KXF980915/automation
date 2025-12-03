pipeline {
    agent any

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
        booleanParam(
            name: 'RUN_PARALLEL',
            defaultValue: false,
            description: '是否并行执行'
        )
    }

    environment {
        // 环境变量
        PROJECT_PATH = '.'
        PYTHON_PATH = 'python3' // 或指定路径
        ALLURE_HOME = tool name: 'Allure', type: 'com.cloudbees.jenkins.plugins.customtools.CustomTool'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    // Python项目示例
                    sh '${PYTHON_PATH} -m pip install -r requirements.txt'

                    // Java项目示例
                    // sh 'mvn clean install'

                    // Node.js项目示例
                    // sh 'npm install'
                }
            }
        }

        stage('Tests') {
            steps {
                script {
                    // 执行测试
                    sh """
                    ${PYTHON_PATH} -m pytest ${PROJECT_PATH}/tests \
                    --browser=${BROWSER} \
                    --env=${ENVIRONMENT} \
                    --alluredir=${WORKSPACE}/allure-results \
                    ${RUN_PARALLEL == 'true' ? '-n 4' : ''}
                    """
                }
            }
        }

        stage('Reports') {
            steps {
                script {
                    // 生成Allure报告
                    sh "${ALLURE_HOME}/bin/allure generate ${WORKSPACE}/allure-results -o ${WORKSPACE}/allure-report --clean"

                    // 发布报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }
    }

    post {
        always {
            // 清理工作
            cleanWs()

            // 发送通知
            emailext(
                subject: "自动化测试执行完成: ${currentBuild.currentResult}",
                body: """
                项目: ${JOB_NAME}
                构建: ${BUILD_NUMBER}
                状态: ${currentBuild.currentResult}
                详情: ${BUILD_URL}
                """,
                to: '2445806874@qq.com'
            )
        }
    }
}