FROM rayproject/ray:2.9.3.94a6d7-py310
WORKDIR /mzai
COPY platform/python/mzai/jobrunner .
