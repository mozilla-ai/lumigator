ARG RAY_IMAGE
ARG RAY_UID=1000

FROM $RAY_IMAGE

USER 0

RUN dnf install -y dnf-plugins-core python3-dnf-plugin-versionlock \
    && dnf copr enable -y slp/mesa-krunkit \
    && dnf install -y mesa-vulkan-drivers-23.3.5-102.aarch64 \
    && dnf versionlock mesa-vulkan-drivers-23.3.5-102.aarch64

RUN dnf install -y vulkan-tools vulkan-loader

USER 1000
