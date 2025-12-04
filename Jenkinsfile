pipeline {
    agent any

    environment {
        // Python环境配置
        PYTHONPATH = "${WORKSPACE}"
        PYTEST_ALLURE_RESULTS = "${WORKSPACE}/allure-results"
        TEST_ENV = "test"
    }

    stages {
        stage('检出代码') {
            steps {
                checkout scm
            }
        }

        stage('环境准备') {
            steps {
                script {
                    // 检查Python环境
                    sh 'python --version'

                    // 创建虚拟环境（可选）
                    sh '''
                        python -m venv venv || true
                        source venv/bin/activate || true
                        pip install --upgrade pip
                    '''

                    // 安装依赖
                    sh 'pip install -r requirements.txt'

                    // 检查依赖
                    sh 'pip list'
                }
            }
        }

        stage('代码检查') {
            steps {
                script {
                    // 运行静态检查
                    sh 'python -m py_compile common/*.py test_case/*.py || true'

                    // 检查YAML文件格式
                    sh 'python -c "import yaml; [yaml.safe_load(open(f)) for f in [\"config.yml\"]]" || true'
                }
            }
        }

        stage('运行测试') {
            steps {
                script {
                    // 清理历史报告
                    sh 'rm -rf allure-results allure-report || true'

                    // 运行测试
                    sh '''
                        # 设置测试环境变量
                        export TEST_ENV=${TEST_ENV}

                        # 运行pytest测试
                        python -m pytest \
                            --alluredir=${PYTEST_ALLURE_RESULTS} \
                            --clean-alluredir \
                            -v \
                            --tb=short \
                            -m "not smoke"  # 可以按标记筛选

                        # 检查测试结果
                        TEST_EXIT_CODE=$?
                        echo "测试退出码: $TEST_EXIT_CODE"
                    '''
                }
            }
            post {
                always {
                    // 生成Allure报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }

        stage('后处理') {
            steps {
                script {
                    // 清理临时文件
                    sh '''
                        rm -rf __pycache__ || true
                        rm -rf .pytest_cache || true
                        rm -f extract.yml || true
                    '''

                    // 归档测试结果
                    archiveArtifacts artifacts: 'allure-results/**/*', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            // 清理工作空间
            cleanWs()
        }
        success {
            echo '流水线执行成功！'
        }
        failure {
            echo '流水线执行失败！'
            // 可以添加通知机制
        }
    }
}