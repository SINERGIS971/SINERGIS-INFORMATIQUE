



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
            <FLD NAME="REP" TYPE="Char">{data_in["REP"]}</FLD>
            <FLD NAME="X_DEVODOO" TYPE="Char">{data_in["X_DEVODOO"]}</FLD>
            <FLD NAME="ORDDAT" TYPE="Date">{data_in["ORDDAT"]}</FLD>
            <FLD NAME="BPCORD" TYPE="Char">{data_in["BPCORD"]}</FLD>
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

