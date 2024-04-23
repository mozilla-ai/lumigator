from pants.backend.helm.target_types import HelmDeploymentTarget
from pants.engine.target import StringField

class KubeconfigFileField(StringField):
    alias = "kubeconfig"
    default = "$HOME/.kube/kind-config"
    help = "which config file to use"

def rules():
    return [HelmDeploymentTarget.register_plugin_field(KubeconfigFileField)]
