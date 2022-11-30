export interface Filter<T> {
  field: keyof T
  value?: T[keyof T]
}
