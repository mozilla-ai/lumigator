export enum FeatureFlags {
  ExperimentManagement = 'experimentManagement',
}

const features = {
  [FeatureFlags.ExperimentManagement]: false,
}

export const isFeatureEnabled = (feature: FeatureFlags): boolean => {
  return features[feature]
}

export const setFeatureFlag = (feature: FeatureFlags, value: boolean): void => {
  features[feature] = value
}

export const initFeatureFlags = (queryString: string) => {
  const params = new URLSearchParams(queryString)

  for (const [key, value] of params) {
    if (Object.values(FeatureFlags).includes(key as FeatureFlags)) {
      setFeatureFlag(key as FeatureFlags, value === 'true')
    }
  }
}
