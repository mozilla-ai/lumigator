export type Dataset = {
  created_at: string;
  filename: string;
  format: string;
  generated: boolean;
  generated_by: unknown;
  ground_truth: boolean;
  id: string;
  run_id: string | null;
  size: number;
};
