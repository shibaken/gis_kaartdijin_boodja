export function unique<T> (list: Array<T>, id?: keyof T): Array<T> {
  return list
    .reduce((previous, current) => {
      return current && previous.findIndex(value => {
        const previousComparator = id ? value[id] : value;
        const currentComparator = id ? current[id] : value;
        return previousComparator === currentComparator;
      }) === -1 ? [...previous, current] : previous;
    }, [] as Array<T>);
}
