variable "name_prefix" {
  description = "Prefix used to name resources created by this module."
  type        = string
}

variable "environment" {
  description = "Deployment environment identifier (e.g. dev, stage, prod)."
  type        = string
}

variable "tags" {
  description = "Common tags/labels metadata for managed resources."
  type        = map(string)
  default     = {}
}
