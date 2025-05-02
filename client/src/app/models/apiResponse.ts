export interface ApiResponse<T> {
  details: string;
  response: T; // response can be of type T or a string;
}
