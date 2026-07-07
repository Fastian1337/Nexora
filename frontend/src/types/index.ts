export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  createdAt: string;
  updatedAt: string;
}

export interface BaseEntity {
  id: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
  isDeleted: boolean;
}
