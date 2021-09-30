pipeline {

    agent {
        label "master"
    }

    environment {
        // GLobal Vars
        NAME = "chatbot-search"
        PROJECT= "labs"

        // Config repo managed by ArgoCD details
        
        // Ireland Cluster
        // ARGOCD_CONFIG_REPO = "github.com/WHOAcademy/lxp-config.git"
        // ARGOCD_CONFIG_REPO_PATH = "lxp-deployment/values-test.yaml"
        // ARGOCD_CONFIG_REPO_BRANCH = "master"

        // PROD Cluster
        // ARGOCD_CONFIG_REPO = "github.com/WHOAcademy/lxp-config-prod.git"
        // ARGOCD_CONFIG_REPO_PATH = "lxp-deployment/values-test.yaml"
        // ARGOCD_CONFIG_REPO_BRANCH = "main"

        // Dev Cluster
        ARGOCD_CONFIG_REPO = "github.com/WHOAcademy/lxp-config-dev.git"
        ARGOCD_CONFIG_REPO_PATH = "lxp-deployment/values-test.yaml"
        ARGOCD_CONFIG_STAGING_REPO_PATH = "lxp-deployment/values-staging.yaml"
        ARGOCD_CONFIG_REPO_BRANCH = "main"

        // Job name contains the branch eg ds-app-feature%2Fjenkins-123
        JOB_NAME = "${JOB_NAME}".replace("%2F", "-").replace("/", "-")
        GIT_SSL_NO_VERIFY = true
        SYSTEM_TEST_BRANCH = "master"

        // Credentials bound in OpenShift
        GIT_CREDS = credentials("${OPENSHIFT_BUILD_NAMESPACE}-git-auth")
        NEXUS_CREDS = credentials("${OPENSHIFT_BUILD_NAMESPACE}-nexus-password")
        QUAY_PUSH_SECRET = "who-lxp-imagepusher-secret"

        // Nexus Artifact repo
        NEXUS_REPO_NAME="labs-static"
        NEXUS_REPO_HELM = "helm-charts"
    }

    // The options directive is for configuration that applies to the whole job.
    options {
        buildDiscarder(logRotator(numToKeepStr: '50', artifactNumToKeepStr: '1'))
        timeout(time: 30, unit: 'MINUTES')
        ansiColor('xterm')
    }

    stages {

        stage('Prepare Environment') {
            failFast true
            parallel {
                stage("Release Build") {
                    options {
                        skipDefaultCheckout(true)
                    }
                    agent {
                        node {
                            label "master"
                        }
                    }
                    when {
                        // considering both old "master" and new "main" naming conventions:
                        expression { GIT_BRANCH.startsWith("master") || GIT_BRANCH.startsWith("main") }
                    }
                    steps {
                        script {
                            // External image push registry info
                            env.IMAGE_REPOSITORY = "quay.io"
                            // app name for master is just learning-experience-platform or something
                            env.APP_NAME = "${NAME}".replace("/", "-").toLowerCase()
                            env.TARGET_NAMESPACE = "whoacademy"
                        }
                    }
                }
                stage("Sandbox Build") {
                    options {
                        skipDefaultCheckout(true)
                    }
                    agent {
                        node {
                            label "master"
                        }
                    }
                    when {
                        expression { GIT_BRANCH.startsWith("dev") || GIT_BRANCH.startsWith("feature") || GIT_BRANCH.startsWith("fix") }
                    }
                    steps {
                        script {
                            // Sandbox registry deets
                            env.IMAGE_REPOSITORY = 'image-registry.openshift-image-registry.svc:5000'
                            // ammend the name to create 'sandbox' deploys based on current branch
                            env.APP_NAME = "${GIT_BRANCH}-${NAME}".replace("/", "-").toLowerCase()
                            // DEPLOYEMENT_TO_CHECK = "${GIT_BRANCH}-${NAME}".replace("/", "-").toLowerCase()
                            env.TARGET_NAMESPACE = "labs-dev"
                        }
                    }
                }
            }
        }

        stage("Build (Compile App)") {
            agent {
                node {
                    label "jenkins-agent-python38"
                }
            }
            steps {
                script {
                    env.VERSION = sh(returnStdout: true, script: "grep -oP \"(?<=appVersion:).*\" chart/Chart.yaml").trim()
                    env.ORCHESTRATOR_PACKAGE = "${APP_NAME}-orc-${VERSION}.tar.gz"
                    env.CHIT_CHAT_PACKAGE = "${APP_NAME}-${VERSION}.tar.gz"
                    // env.SECRET_KEY = 'gs7(p)fk=pf2(kbg*1wz$x+hnmw@y6%ij*x&pq4(^y8xjq$q#f' //TODO: get it from secret vault
                }
                sh 'printenv'

                // TODO
                // echo '### Installing deps ###'

                // TODO
                // echo '### Running linter ###'

                // TODO
                // echo '### Running tests ###'


                echo '### Packaging Chit-Chat Service Code for Nexus ###'
                sh '''
                    touch ${CHIT_CHAT_PACKAGE}
                    tar --exclude=${CHIT_CHAT_PACKAGE} \
                        --exclude='.git/*' \
                        --exclude='production_data/vla_data_no_variations' \
                        --exclude='production_data/chitchat.bin' \
                        --exclude='production_data/chitchat_emoji_faq.bin' \
                        -C ./ -zcvf ${CHIT_CHAT_PACKAGE} .
                    curl -v -f -u ${NEXUS_CREDS} --upload-file ${CHIT_CHAT_PACKAGE} \
                        http://${SONATYPE_NEXUS_SERVICE_SERVICE_HOST}:${SONATYPE_NEXUS_SERVICE_SERVICE_PORT}/repository/${NEXUS_REPO_NAME}/${APP_NAME}/${CHIT_CHAT_PACKAGE}
                '''
            }
            // Post can be used both on individual stages and for the entire build.
            post {
                always {
                    echo ''  // TODO
                    // // archiveArtifacts "**"
                    // junit 'xunittest.xml'
                    // // publish html
                    // publishHTML target: [
                    //     allowMissing: false,
                    //     alwaysLinkToLastBuild: false,
                    //     keepAll: true,
                    //     reportDir: 'cover',
                    //     reportFiles: 'index.html',
                    //     reportName: 'Django Code Coverage'
                    // ]
                }
            }
        }

        stage("Bake (OpenShift Build)") {
            options {
                skipDefaultCheckout(true)
                timeout(time: 40, unit: 'MINUTES')  // timeout on this stage
            }
            agent {
                node {
                    label "master"
                }
            }
            steps {
                sh 'printenv'
                echo '### Get Binary from Nexus and shove it in a box ###'

                echo '### Chit-Chat ###'
                sh  '''
                    rm -rf ${CHIT_CHAT_PACKAGE}
                    curl -v -f -u ${NEXUS_CREDS} http://${SONATYPE_NEXUS_SERVICE_SERVICE_HOST}:${SONATYPE_NEXUS_SERVICE_SERVICE_PORT}/repository/${NEXUS_REPO_NAME}/${APP_NAME}/${CHIT_CHAT_PACKAGE} -o ${CHIT_CHAT_PACKAGE}
                    BUILD_ARGS=" --build-arg git_commit=${GIT_COMMIT} --build-arg git_url=${GIT_URL}  --build-arg build_url=${RUN_DISPLAY_URL} --build-arg build_tag=${BUILD_TAG}"
                    echo ${BUILD_ARGS}
                    oc delete bc ${APP_NAME} || rc=$?
                    if [[ $TARGET_NAMESPACE == *"dev"* ]]; then
                        echo "🏗 Creating a sandbox build for inside the cluster 🏗"
                        oc new-build --binary --name=${APP_NAME} -l app=${APP_NAME} ${BUILD_ARGS} --strategy=docker || rc=$?
                        oc start-build ${APP_NAME} --from-archive=${CHIT_CHAT_PACKAGE} ${BUILD_ARGS} --follow
                        # used for internal sandbox build ....
                        oc tag ${OPENSHIFT_BUILD_NAMESPACE}/${APP_NAME}:latest ${TARGET_NAMESPACE}/${APP_NAME}:${VERSION}
                    else
                        echo "🏗 Creating a potential build that could go all the way so pushing externally 🏗"
                        oc new-build --binary --name=${APP_NAME} -l app=${APP_NAME} ${BUILD_ARGS} --strategy=docker --push-secret=${QUAY_PUSH_SECRET} --to-docker --to="${IMAGE_REPOSITORY}/${TARGET_NAMESPACE}/${APP_NAME}:${VERSION}"
                        oc set build-secret --pull bc/${APP_NAME} ${QUAY_PUSH_SECRET}
                        oc start-build ${APP_NAME} --from-archive=${CHIT_CHAT_PACKAGE} ${BUILD_ARGS} --follow
                    fi
                '''
            }
        }

  stage("Helm Package App (master)") {
            agent {
                node {
                    label "jenkins-agent-helm"
                }
            }
            steps {
                sh 'printenv'
                sh '''
                    # might be overkill...
                    yq e '.appVersion = env(VERSION)' -i chart/Chart.yaml
                    yq e '.version = env(VERSION)' -i chart/Chart.yaml
                    yq e '.name = env(APP_NAME)' -i chart/Chart.yaml

                    # Chit-Chat
                    # probs point to the image inside ocp cluster or perhaps an external repo?
                    yq e '.search.image_repository = env(IMAGE_REPOSITORY)' -i chart/values.yaml
                    yq e '.search.image_name = env(APP_NAME)' -i chart/values.yaml
                    yq e '.search.image_namespace = env(TARGET_NAMESPACE)' -i chart/values.yaml
                    # latest built image
                    yq e '.search.image_tag = env(VERSION)' -i chart/values.yaml
                '''
                sh 'printenv'
                sh '''
                    # package and release helm chart?
                    helm package chart/ --app-version ${VERSION} --version ${VERSION} --dependency-update
                    curl -v -f -u ${NEXUS_CREDS} http://${SONATYPE_NEXUS_SERVICE_SERVICE_HOST}:${SONATYPE_NEXUS_SERVICE_SERVICE_PORT}/repository/${NEXUS_REPO_HELM}/ --upload-file ${APP_NAME}-${VERSION}.tgz
                '''
            }
        }

        stage("Deploy App") {
            failFast true
            parallel {
                stage("sandbox - helm3 publish and install"){
                    options {
                        skipDefaultCheckout(true)
                    }
                    agent {
                        node {
                            label "jenkins-agent-helm"
                        }
                    }
                    when {
                        expression { GIT_BRANCH.startsWith("dev") || GIT_BRANCH.startsWith("feature") || GIT_BRANCH.startsWith("fix") }
                    }
                    steps {
                        // TODO - if SANDBOX, create release in rando ns
                        sh 'printenv'
                        sh 'ls'
                        sh '''
                            helm uninstall ${APP_NAME} --namespace=${TARGET_NAMESPACE} || rc=$?
                            curl -v -f -u ${NEXUS_CREDS} http://${SONATYPE_NEXUS_SERVICE_SERVICE_HOST}:${SONATYPE_NEXUS_SERVICE_SERVICE_PORT}/repository/${NEXUS_REPO_HELM}/${APP_NAME}-${VERSION}.tgz -o ${APP_NAME}-${VERSION}.tgz
                            sleep 40
                            helm upgrade --install ${APP_NAME} \
                                --namespace=${TARGET_NAMESPACE} \
                                ${APP_NAME}-${VERSION}.tgz
                        '''
                    }
                }
                stage('test env - ArgoCD sync') {
                    options {
                        skipDefaultCheckout(true)
                    }
                    agent {
                        node {
                            label 'jenkins-agent-argocd'
                        }
                    }
                    when {
                        expression { GIT_BRANCH.startsWith('main') }
                    }
                    steps {
                        echo '### Commit new image tag to git ###'
                        sh  '''
                            git clone https://${GIT_CREDS_USR}:${GIT_CREDS_PSW}@${ARGOCD_CONFIG_REPO} config-repo
                            cd config-repo
                            git checkout ${ARGOCD_CONFIG_REPO_BRANCH}
                            # yq - Select and update matching values in map
                            # https://mikefarah.gitbook.io/yq/v/v4.x/operators/select#select-and-update-matching-values-in-map
                            yq e '(.applications.[] |= select(.name == ("test-" + env(NAME))) |= .source_ref = env(VERSION)' -i $ARGOCD_CONFIG_REPO_PATH
                            git config --global user.email "jenkins@rht-labs.bot.com"
                            git config --global user.name "Jenkins"
                            git config --global push.default simple
                            git add ${ARGOCD_CONFIG_REPO_PATH}
                            git commit -m "🚀 AUTOMATED COMMIT - Deployment of ${APP_NAME} at version ${VERSION} 🚀" || rc=$?
                            git remote set-url origin  https://${GIT_CREDS_USR}:${GIT_CREDS_PSW}@${ARGOCD_CONFIG_REPO}
                            git push -u origin ${ARGOCD_CONFIG_REPO_BRANCH}
                            # Give ArgoCD a moment to gather it's thoughts and roll out a deployment before Jenkins races on to test things
                            # issue here is an asynchronous pipline (argo) intreacting with a synchronous job ie jenkins
                            sleep 20
                        '''
                    }
                }
            }
        }

        stage('Trigger System Tests') {
            options {
                skipDefaultCheckout(true)
            }
            agent {
                node {
                    label 'master'
                }
            }
            when {
                expression { GIT_BRANCH.startsWith('main') }
            }
            steps {
                sh  '''
                    echo "TODO - Run tests"
                '''
                build job: "system-tests/${SYSTEM_TEST_BRANCH}", parameters: [[$class: 'StringParameterValue', name: 'APP_NAME', value: "${APP_NAME}" ], [$class: 'StringParameterValue', name: 'VERSION', value: "${VERSION}"]], wait: false
            }
        }

        // stage("Validate Deployment") {
        //     failFast true
        //     parallel {
        //         stage("sandbox - validate deployment"){
        //             options {
        //                 skipDefaultCheckout(true)
        //             }
        //             agent {
        //                 node {
        //                     label "master"
        //                 }
        //             }
        //             when {
        //                 expression { GIT_BRANCH.startsWith("dev") || GIT_BRANCH.startsWith("feature") || GIT_BRANCH.startsWith("fix") }
        //             }
        //             steps {
        //                 sh '''
        //                    set +x
        //                    COUNTER=0
        //                    DELAY=5
        //                    MAX_COUNTER=80
        //                    echo "Validating deployment of ${APP_NAME} in project ${TARGET_NAMESPACE}"
        //                    LATEST_DC_VERSION=\$(oc get dc ${APP_NAME} -n ${TARGET_NAMESPACE} --template='{{ .status.latestVersion }}')
        //                    RC_NAME=${APP_NAME}-\${LATEST_DC_VERSION}
        //                    set +e
        //                    while [ \$COUNTER -lt \$MAX_COUNTER ]
        //                    do
        //                      RC_ANNOTATION_RESPONSE=\$(oc get rc -n ${TARGET_NAMESPACE} \$RC_NAME --template="{{.metadata.annotations}}")
        //                      echo "\$RC_ANNOTATION_RESPONSE" | grep openshift.io/deployment.phase:Complete >/dev/null 2>&1
        //                      if [ \$? -eq 0 ]; then
        //                        echo "Deployment Succeeded!"
        //                        break
        //                      fi
        //                      echo "\$RC_ANNOTATION_RESPONSE" | grep -E 'openshift.io/deployment.phase:Failed|openshift.io/deployment.phase:Cancelled' >/dev/null 2>&1
        //                      if [ \$? -eq 0 ]; then
        //                        echo "Deployment Failed"
        //                        exit 1
        //                      fi
        //                      if [ \$COUNTER -lt \$MAX_COUNTER ]; then
        //                        echo -n "."
        //                        COUNTER=\$(( \$COUNTER + 1 ))
        //                      fi
        //                      if [ \$COUNTER -eq \$MAX_COUNTER ]; then
        //                        echo "Max Validation Attempts Exceeded. Failed Verifying Application Deployment..."
        //                        exit 1
        //                      fi
        //                      sleep \$DELAY
        //                    done
        //                    set -e
        //                 '''
        //             }
        //         }
        //     }
        // }
    }
}