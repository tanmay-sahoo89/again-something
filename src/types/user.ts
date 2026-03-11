export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  createdAt?: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}
