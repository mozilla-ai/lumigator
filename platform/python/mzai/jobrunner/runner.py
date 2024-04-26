from mzai.schemas.jobs import JobConfig


class JobRunner:
    def run(self, config: JobConfig):
        try:
            print(config)
        except Exception as e:
            print(e)
