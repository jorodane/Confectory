"""Generated Office fixture; no user or external bytes."""
import io,zipfile
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
pkg='http://schemas.openxmlformats.org/package/2006/relationships'
workbook=f'<workbook xmlns="{ns}" xmlns:r="{rel}"><bookViews><workbookView activeTab="0"/></bookViews><sheets><sheet name="Main" sheetId="1" r:id="rId1"/><sheet name="Locked" sheetId="2" r:id="rId2"/><sheet name="Empty" sheetId="3" r:id="rId3"/><sheet name="FormulaOther" sheetId="4" r:id="rId4"/></sheets><calcPr calcId="keep"/><extLst><ext uri="keep"/></extLst></workbook>'
relationships=f'<Relationships xmlns="{pkg}">'+''.join(f'<Relationship Id="rId{i}" Type="{rel}/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,5))+f'<Relationship Id="not-a-sheet" Type="{rel}/hyperlink" Target="https://must-not-load.invalid" TargetMode="External"/></Relationships>'
sheet=f'<worksheet xmlns="{ns}"><dimension ref="A1:H3"/><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetData><row r="1" spans="1:8"><c r="A1" t="s" s="1"><v>0</v></c><c r="B1" t="n" s="2"><v>1.5</v></c><c r="C1" t="b"><v>1</v></c><c r="D1"><f>B1*2</f><v>3</v></c><c r="E1" t="inlineStr"><is><t>merge</t></is></c><c r="F1" t="inlineStr"><is><t>covered</t></is></c><c r="H1" s="5"><v>10</v></c></row><row r="3"><c r="A3" t="inlineStr"><is><t>second row</t></is><extLst><ext uri="cell-keep"/></extLst></c></row></sheetData><mergeCells count="1"><mergeCell ref="E1:F1"/></mergeCells><hyperlinks><hyperlink ref="A3" location="Main!A1"/></hyperlinks></worksheet>'
parts={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/></Types>','_rels/.rels':f'<Relationships xmlns="{pkg}"><Relationship Id="root" Type="{rel}/officeDocument" Target="xl/workbook.xml"/></Relationships>','xl/workbook.xml':workbook,'xl/_rels/workbook.xml.rels':relationships,'xl/worksheets/sheet1.xml':sheet,'xl/worksheets/sheet2.xml':f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>protected sheet</t></is></c></row></sheetData><sheetProtection sheet="1" password="keep"/></worksheet>','xl/worksheets/sheet3.xml':f'<worksheet xmlns="{ns}"><sheetData/></worksheet>','xl/worksheets/sheet4.xml':f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1"><f>1+1</f><v>2</v></c></row></sheetData></worksheet>','xl/sharedStrings.xml':f'<sst xmlns="{ns}" count="1" uniqueCount="1"><si><r><rPr><b/></rPr><t>original 🙂 sheet</t></r></si></sst>','xl/styles.xml':'<styles keep="original"/>','xl/media/image.bin':bytes([0,255,17,84]),'docProps/custom.xml':'<custom>retained</custom>'}
def archive(values=parts):
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  z.comment=b'original-package-comment'
  for name,data in values.items():
   info=zipfile.ZipInfo(name,(2024,1,2,3,4,6));info.compress_type=zipfile.ZIP_DEFLATED;info.comment=b'entry-retained';info.extra=b'\xfe\xca\x00\x00';z.writestr(info,data.encode() if isinstance(data,str) else data)
 return out.getvalue()
raw=archive()
