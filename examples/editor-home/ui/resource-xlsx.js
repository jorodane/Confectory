import {createResourceDocx} from './resource-docx.js';
import {xlsxDocument,editedXlsxXML,renderXlsxEditor} from './resource-xlsx-dom.js';
const mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
export const editableXlsx=item=>item.kind!=='image'&&(item.type===mime||['','application/octet-stream','application/zip'].includes(item.type||'')&&/\.xlsx$/i.test(item.name));
export const createResourceXlsx=api=>createResourceDocx(api,{id:'xlsx',codec:'xlsx-v1',subject:'셀',label:'XLSX',maxChanges:4096,document:xlsxDocument,edit:editedXlsxXML,render:renderXlsxEditor,description:'셀 값만 수정합니다. 수식·병합 구조는 유지되며 수식 계산은 원본 프로그램에서 갱신됩니다.',budgetText:'셀 변경은 최대 4,096개·합계 98,304자까지 보관할 수 있어요. 입력은 화면에 유지됩니다. 닫기 전에 길이나 개수를 줄여 주세요.'});
