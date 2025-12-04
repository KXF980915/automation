pipeline {
    agent {
        label 'windows'  // 必须使用Windows节点
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['dev', 'test', 'prod'],
            description: '选择测试环境'
        )
        string(
            name: 'TEST_MARK',
            defaultValue: '',
            description: '测试标记（如smoke）'
        )
    }

    stages {
        stage('准备') {
            steps {
                bat '''
                    echo 清理工作空间...
                    if exist allure-results rmdir /s /q allure-results
                    if exist allure-report rmdir /s /q allure-report
                    if exist __pycache__ rmdir /s /q __pycache__

                    echo 检出代码...
                    git clean -fdx
                '''
            }
        }

        stage('安装依赖') {
            steps {
                bat '''
                    echo 安装Python依赖...
                    pip install -r requirements.txt
                '''
            }
        }

        stage('运行测试') {
            steps {
                bat """
                    echo 设置环境变量...
                    set TEST_ENV=${params.TEST_ENV}

                    echo 运行测试...
                    python -m pytest test_case ^
                        -v ^
                        --tb=short ^
                        --alluredir=.\\allure-results ^
                        --clean-alluredir ^
                        ${params.TEST_MARK ? '-m ' + params.TEST_MARK : ''}
                """
            }
        }

        stage('生成报告') {
            steps {
                bat '''
                    echo 生成Allure报告...
                    allure generate allure-results -o allure-report --clean

                    echo 归档报告...
                    if not exist archive mkdir archive
                    copy allure-report\\index.html archive\\test-report-${BUILD_NUMBER}.html
                '''
            }
        }
    }

    post {
        always {
            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'allure-results']]
            ])

            // 清理Python缓存
            bat '''
                del /f /q extract.yml 2>nul
                rmdir /s /q .pytest_cache 2>nul
                del /f /q *.pyc 2>nul
            '''
        }

        success {
            echo '✓ 测试执行成功！'
        }

        failure {
            echo '✗ 测试执行失败！'
        }
    }
}