// Authored resource kinds are private view preferences, never access grants.
export const resourceKindChoices=Object.freeze([['all','모든 자료'],['document','문서'],['image','그림'],['mesh','메시'],['file','기타 파일']].map(Object.freeze));
export function resourceFilterValue(value){return typeof value==='string'&&resourceKindChoices.some(([kind])=>kind===value)?value:'all';}
export function resourceMatchesFilter(item,value){const filter=resourceFilterValue(value);return filter==='all'||item.kind==='folder'||item.kind===filter;}
