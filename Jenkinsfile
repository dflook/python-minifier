#!groovy

pipeline {
    agent none

    stages {
        stage('xtest') {
            parallel {
                stage('python27') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python27 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python33') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora28-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install 'tox<3' 'virtualenv<16'
                        tox -r -e python33 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python34') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python34 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python35') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python35 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python36') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python36 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python37') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2020-05-03'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python37 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python38') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2019-10-20'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e python38 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('python39') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora32-2020-10-11'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.20
                        tox -r -e python39 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
                stage('pypy3') {
                    agent {
                        docker {
                            image 'danielflook/python-minifier-build:fedora30-2019-10-20'
                            args "-u 0:0 --entrypoint '' --init"
                        }
                    }
                    steps {
                        cleanWs()
                        checkout scm
                        sh '''#!/bin/bash -e
                        VERSION=$(python3 setup.py --version)
                        sed -i "s/setup_requires=.*/version='$VERSION',/; s/use_scm_version=.*//" setup.py
                        pip3 install tox==3.11.1 virtualenv==16.6.0
                        tox -r -e pypy3 xtest
                        '''
                    }
                    post {
                        always {
                            junit '**/junit-*.xml'
                        }
                    }
                }
            }
        }
    }
}
