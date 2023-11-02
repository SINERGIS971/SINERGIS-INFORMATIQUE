



# Permet de générer le code SOAP afin de générer la commande dans X3
# pool_alias : Nom du pool crée dans X3
# public_name : Nom du web service
# code_lang : Code le la langue pour la réponse, par défaut à FRA (français)
def order_to_soap(data_in,pool_alias,public_name,code_lang="FRA"):
    i = 1 # Numéro de la ligne en cours d'écriture
    data_lines = []
    for line in data_in["lines"]:
        data_lines.append(
            f"""
            <LIN NUM="{str(i)}">
            <FLD NAME="ITMREF" TYPE="Char">{line["ITMREF"]}</FLD>
            <FLD NAME="ITMDES" TYPE="Char">{line["ITMDES"]}</FLD>
            <FLD NAME="QTY" TYPE="Decimal">{line["QTY"]}</FLD>
            <FLD NAME="GROPRI" TYPE="Decimal">{line["GROPRI"]}</FLD>
            <FLD NAME="DISCRGVAL1" TYPE="Decimal">{line["DISCRGVAL1"]}</FLD>
            <FLD NAME="CPRPRI" TYPE="Decimal">{line["CPRPRI"]}</FLD>
            </LIN>
            """
        )
        i += 1

    data=f"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wss="http://www.adonix.com/WSS" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
        <soapenv:Header/>
        <soapenv:Body>
            <wss:save soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <callContext xsi:type="wss:CAdxCallContext">
                <codeLang xsi:type="xsd:string">{code_lang}</codeLang>
                <poolAlias xsi:type="xsd:string">{pool_alias}</poolAlias>
                <poolId xsi:type="xsd:string"></poolId>
                <requestConfig xsi:type="xsd:string"></requestConfig>
            </callContext>
            <publicName xsi:type="xsd:string">{public_name}</publicName>
            <objectXml xsi:type="xsd:string">
            <![CDATA[<?xml version="1.0" encoding="UTF-8"?>
            <PARAM>
            <GRP ID="SOH0_1">
            <FLD NAME="SALFCY" TYPE="Char">{data_in["SALFCY"]}</FLD>
            <FLD NAME="SOHTYP" TYPE="Char">{data_in["SOHTYP"]}</FLD>
            <FLD NAME="CUSORDREF" TYPE="Char">{data_in["CUSORDREF "]}</FLD>
            <FLD NAME="X_DEVODOO" TYPE="Char">{data_in["X_DEVODOO"]}</FLD>
            <FLD NAME="ORDDAT" TYPE="Date">{data_in["ORDDAT"]}</FLD>
            <FLD NAME="BPCORD" TYPE="Char">{data_in["BPCORD"]}</FLD>
            </GRP>
            <GRP ID="SOH1_3">
                    <LST NAME="REP" SIZE="2" TYPE="Char">
                        <ITM>{data_in["REP"]}</ITM>
                    </LST>
            </GRP>
            <TAB DIM="200" ID="SOH4_1" SIZE="{len(data_lines)}">
            {''.join(data_lines)}
            </TAB>
            </PARAM>
            ]]>
            </objectXml>
        </wss:save>
    </soapenv:Body>
    </soapenv:Envelope>
    """
    return data

def order_line_text_to_soap (SOHNUM,total_text,num_line,pool_alias,public_name,code_lang="FRA"):
    total_text = total_text.replace("<","")
    total_text = total_text.replace(">","")
    total_text = total_text.replace("\xa0","")
    total_text = total_text.replace("\n"," ")
    words = total_text.split()
    results = []
    line = ""

    for word in words :
        if len(line) + len(word) + 1 <= 220:
            line += word+" "
        else:
            results.append(line.strip())
            line = " "+word+" "
    if line:
        results.append(line.strip())

    tab = []
    j = 1
    for text in results:
        tab.append(f"""
        <LIN NUM="{j}">
        <FLD NAM="ZTEXTE" >{text}</FLD>
        </LIN>
        """)
        j += 1
        if j == 6 :
            break;
    data=f"""
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wss="http://www.adonix.com/WSS">
   <soapenv:Header/>
   <soapenv:Body>
      <wss:run soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <callContext xsi:type="wss:CAdxCallContext">
            <codeLang xsi:type="xsd:string">{code_lang}</codeLang>
            <poolAlias xsi:type="xsd:string">{pool_alias}</poolAlias>
            <poolId xsi:type="xsd:string"></poolId>
            <requestConfig xsi:type="xsd:string"></requestConfig>
         </callContext>
         <publicName xsi:type="xsd:string">{public_name}</publicName>
         <inputXml xsi:type="xsd:string">
         <![CDATA[<PARAM>
		<GRP ID="GRP1" NAM="GRP1">
		<FLD NAM="ZNUMSOH">{SOHNUM}</FLD>
		<FLD NAM="ZLIG">{num_line}000</FLD>
		</GRP>
		<TAB ID="GRP2" DIM="5">
		{''.join(tab)}
		</TAB>
		</PARAM>]]>
         </inputXml>
      </wss:run>
    </soapenv:Body>
    </soapenv:Envelope>
    """
    return data

# Fonction qui permet de créer une requête SOAP avec toutes les activités du client en un requête SOAP
# Le client doit être unique.

def actions_to_soap(datas,pool_alias,public_name,code_lang="FRA"):
    if len(data) < 1 :
        return False
    
    # Chargement du transcodage
    #action_ids = self.env["sinergis.myactions"].search([('client','=',partner_id.id)], limit=1)
    #datas = [action_to_dict(action_id, company_id_transcode, user_transcode) for action_id in action_ids]
    #Structuration des lignes

    # Chargement des données de société
    SALFCY = datas[0]['SALFCY']
    ODOOCLIENTID = datas[0]['ODOOCLIENTID']
    BPCORD = datas[0]['BPCORD']
    CLIENT_NAME = datas[0]['CLIENT_NAME']

    lines = []
    i = 0
    for data in datas:
        i+=1
        lines.append(f"""<LIN NUM='{str(i)}'>
                <FLD NAME='ODOO_ID' TYPE='Char'>{data['ODOO_ID']}</FLD>
                <FLD NAME='REP' TYPE='Char'>{data['REP']}</FLD>
                <FLD NAME='CATEGORIE' TYPE='Char'>{data['CATEGORIE']}</FLD>
                <FLD NAME='BILLING_TYPE' TYPE='Char'>{data['BILLING_TYPE']}</FLD>
                <FLD NAME='ITEMLINEODOO' TYPE='Char'>{data['ITEMLINEODOO']}</FLD>
                <FLD NAME='OBJET' TYPE='Char'>{data['CATEGORIE']}</FLD>
                <FLD NAME='QTY' TYPE='Decimal'>{data['QTY']}</FLD>
                <FLD NAME='UNITE' TYPE='Char'>{data['UNITE']}</FLD>
                <FLD NAME='NUM_BDC' TYPE='Char'>{data['NUM_BDC']}</FLD>
                <FLD NAME='DATE_BDC' TYPE='Date'>
                    {data['DATE_BDC']}
                </FLD>
                <FLD NAME='PRODUCT' TYPE='Char'>{data['PRODUCT']}</FLD>
                <FLD NAME='SUBPRODUCT' TYPE='Char'>{data['SUBPRODUCT']}</FLD>
                <FLD NAME='XTYPE' TYPE='Char'>{data['XTYPE']}</FLD>
                <FLD NAME='START' TYPE='Date'>{data['START']}</FLD>
                <FLD NAME='ENDDAT' TYPE='Date'>{data['ENDDAT']}</FLD>
                <FLD NAME='FACT' TYPE='Char'>{data['FACT']}</FLD>
                <FLD MENULAB='' MENULOCAL='1' NAME='PROJET' TYPE='Integer'>0</FLD>
                <FLD NAME='WRITE_DATE' TYPE='Date'>
                    {data['WRITE_DATE']}
                </FLD>
                </LIN>""")
    request = f"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wss="http://www.adonix.com/WSS" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
        <soapenv:Header/>
        <soapenv:Body>
            <wss:save soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <callContext xsi:type="wss:CAdxCallContext">
                <codeLang xsi:type="xsd:string">FRA</codeLang>
                <poolAlias xsi:type="xsd:string">{pool_alias}</poolAlias>
                <poolId xsi:type="xsd:string"></poolId>
                <requestConfig xsi:type="xsd:string"></requestConfig>
            </callContext>
            <publicName xsi:type="xsd:string">{public_name}</publicName>
            <objectXml xsi:type="xsd:string">
            <![CDATA[<?xml version="1.0" encoding="UTF-8"?>
            <PARAM>
            <GRP ID="XOA1_1">
                <FLD NAME="SALFCY" TYPE="Char">{SALFCY}</FLD>
                <FLD NAME="ODOOCLIENTID" TYPE="Char">{ODOOCLIENTID}</FLD>
                <FLD NAME="BPCORD" TYPE="Char">{BPCORD}</FLD>
                <FLD NAME="CLIENT_NAME" TYPE="Char">{CLIENT_NAME}</FLD>
            </GRP>
                <TAB DIM="10" ID="XOA1_2" SIZE="1">
                    {''.join(lines)}
                </TAB>
            </PARAM>
            ]]>
            </objectXml>
        </wss:save>
    </soapenv:Body>
    </soapenv:Envelope>
    """
    return request