<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - ACK)
		Input : 			ACK ICSR File compliant with E2B(R2)
		Output : 		ACK ICSR File compliant with E2B(R3)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)
		
		Version:		0.9.2
		Date:			20/10/2015
		Status:		Draft
		Author:		Nick Halsey (EU)

-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	<xsl:include href="upgrade.xsl"/>
	
	<xsl:output indent="yes" method="xml" omit-xml-declaration="no" encoding="utf-8"/>
	<xsl:strip-space elements="*"/>
	<xsl:strip-space elements="*"/>

	<!-- ICH ICSR : conversion of the main structure incl. root element and controlActProcess
	E2B(R2): root element "ichicsr"
	E2B(R3): root element "PORR_IN049016UV"
	-->
	<xsl:template match="/">
		<MCCI_IN200101UV01 ITSVersion="XML_1.0">
			<xsl:attribute name="xsi:schemaLocation">urn:hl7-org:v3 http://eudravigilance.ema.europa.eu/xsd/multicacheschemas/MCCI_IN200101UV01.xsd</xsl:attribute>
			<!-- ACK.M - Message Header (Header) -->
			<xsl:apply-templates select="/ichicsrack/ichicsrmessageheader" mode="header-1"/>
			<xsl:for-each select="/ichicsrack/acknowledgment/reportacknowledgment">
				<MCCI_IN000002UV01>
					<!-- B - Report Acknowledgment (Part I) -->
					<xsl:apply-templates select="." mode="ack-1"/>
					<!-- ACK.M - Message Header (Sender & Receiver) -->
					<xsl:apply-templates select="/ichicsrack/ichicsrmessageheader" mode="header-2"/>
					<!-- B - Report Acknowledgment (Part II) -->
					<xsl:apply-templates select="." mode="ack-2"/>
				</MCCI_IN000002UV01>
			</xsl:for-each>
			<!-- ACK.M - Message Header (Sender & Receiver) -->
			<xsl:apply-templates select="/ichicsrack/ichicsrmessageheader" mode="header-3"/>
			<!-- ACK.A - Message Acknowledgment -->
			<xsl:apply-templates select="/ichicsrack/acknowledgment/messageacknowledgment"/>
		</MCCI_IN200101UV01>
	</xsl:template>
	
	<!-- ACK.M - ACK Batch Header (Part I) -->
	<xsl:template match="ichicsrmessageheader" mode="header-1">
		<!-- ACK.M.1 - ACK Batch Number -->
		<id extension="{messagenumb}" root="{$oidAckBatchNumber}"/>
		<!-- ACK.M.4 - ACK Date of Batch Transmission -->
		<creationTime value="{messagedate}"/>
		<responseModeCode code="D"/>
		<interactionId extension="MCCI_IN200101UV01" root="2.16.840.1.113883.1.18"/>
	</xsl:template>
	
	<!-- ACK.M - ACK Batch Header (Part II) -->
	<xsl:template match="ichicsrmessageheader" mode="header-2">
		<!-- ACK.M.4 - ACK Date of Batch Transmission -->
		<creationTime value="{messagedate}"/>
		<interactionId extension="MCCI_IN000002UV01" root="2.16.840.1.113883.1.18"/>
		<processingCode code="P"/>
		<processingModeCode code="T"/>
		<acceptAckCode code="NE"/>
		<receiver typeCode="RCV">
			<device classCode="DEV" determinerCode="INSTANCE">
				<!-- ACK.B.r.3: ICSR Message Receiver Identifier -->
				<id extension="{../acknowledgment/messageacknowledgment/icsrmessagereceiveridentifier}" root="{$oidAckReceiverID}"/>
			</device>
		</receiver>
		<sender typeCode="SND">
			<device classCode="DEV" determinerCode="INSTANCE">
				<!-- ACK.B.r.4: ICSR Message Sender Identifier -->
				<id extension="{../acknowledgment/messageacknowledgment/icsrmessagesenderidentifier}" root="{$oidAckSenderID}"/>
			</device>
		</sender>
	</xsl:template>
	
	<!-- ACK.M - ACK Batch Header (Sender & Receiver) -->
	<xsl:template match="ichicsrmessageheader" mode="header-3">
		<receiver typeCode="RCV">
			<device classCode="DEV" determinerCode="INSTANCE">
				<!-- ACK.M.3: ACK Batch Receiver Identifier -->
				<id extension="{messagereceiveridentifier}" root="{$oidAckBatchReceiverID}"/>
			</device>
		</receiver>
		<sender typeCode="SND">
			<device classCode="DEV" determinerCode="INSTANCE">
				<!-- ACK.M.2: ACK Batch Sender Identifier -->
				<id extension="{messagesenderidentifier}" root="{$oidAckBatchSenderID}"/>
			</device>
		</sender>
	</xsl:template>
	
	<!-- ACK.B - Report Acknowledgment (Part I) -->
	<xsl:template match="reportacknowledgment" mode="ack-1">
		<id extension="{localreportnumb}" root="{$oidLocalReportNumber}"/>
		<!--ACK.B.r.2 Local Report Number -->
	</xsl:template>
	
	<!-- ACK.B - Report Acknowledgment (Part II) -->
	<xsl:template match="reportacknowledgment" mode="ack-2">
	<!-- ACK.B.r.5 - Receipt date -Not converted -->
		<!-- <xsl:if test="string-length(receiptdate) > 0">
			<attentionLine>
				<keyWordText code="{$receiptDate}" codeSystem="{$oidDateOfCreation}"/>
				<value xsi:type="TS" value="{receiptdate}"/>
			</attentionLine>
		</xsl:if> -->
		
		<xsl:variable name="code">
			<xsl:choose>
				<xsl:when test="reportacknowledgmentcode = '01' or reportacknowledgmentcode = '1'">CA</xsl:when>
				<xsl:otherwise>CR</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<!-- ACK.B.r.6 - Acknowledgement Report Code -->
		<acknowledgement typeCode="{$code}">
			<targetMessage>
				<id extension="{safetyreportid}" root="{$oidMessageNumber}"/>
		<!--ACK.B.r.1 - Safety Report ID ICSR Message Number -->
			</targetMessage>
			<xsl:if test="string-length(errormessagecomment) > 0">
				<acknowledgementDetail>
					<!-- ACK.B.r.7 - Error/Warning message / comment -->
					<text><xsl:value-of select="errormessagecomment"/></text>
				</acknowledgementDetail>
			</xsl:if>
		</acknowledgement>
	</xsl:template>

		<!--xsl:if test="string-length(icsrmessagesenderidentifier) > 0">
			<attentionLine>
				<keyWordText code="{$icsrMessageSenderIdentifier}"/>
				<value xsi:type="ST"><xsl:value-of select="icsrmessagesenderidentifier"/></value>
			</attentionLine>
		</xsl:if>
		<xsl:if test="string-length(icsrmessagereceiveridentifier) > 0">
			<attentionLine>
				<keyWordText code="{$icsrMessageReceiverIdentifier}"/>
				<value xsi:type="ST"><xsl:value-of select="icsrmessagereceiveridentifier"/></value>
			</attentionLine>
		</xsl:if-->

	
	<!-- ACK.A - Message Acknowledgment (Message) -->
	<xsl:template match="messageacknowledgment">
		<!-- ACK.A.2 - Local Message Number -->
		<xsl:if test="string-length(localmessagenumb) > 0">
			<attentionLine>
				<keyWordText code="{$AckLocalMessageNumber}" codeSystem="{$oidAttentionLineCode}"/>
				<value xsi:type="II" extension="{localmessagenumb}" root="{$oidAckLocalMessageNumber}"/>
			</attentionLine>
		</xsl:if>
		<!-- ACK.A.3 - Date of ICSR Batch Transmission -->
		<xsl:if test="string-length(icsrmessagedate) > 0">
			<attentionLine>
				<keyWordText code="{$DateOfIcsrBatchTransmission}" codeSystem="{$oidAttentionLineCode}"/>
				<value xsi:type="TS" value="{icsrmessagedate}"/>
			</attentionLine>
		</xsl:if>
		<!-- ACK.A.4- Transmission Acknowledgment Code -->
		<xsl:variable name="code">
			<xsl:choose>
				<xsl:when test="transmissionacknowledgmentcode = '01' or transmissionacknowledgmentcode = '1'">AA</xsl:when>
				<xsl:when test="transmissionacknowledgmentcode = '02' or transmissionacknowledgmentcode = '2'">AE</xsl:when>
				<xsl:when test="transmissionacknowledgmentcode = '03' or transmissionacknowledgmentcode = '3'">AR</xsl:when>
				<xsl:otherwise>AR</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<acknowledgement typeCode="{$code}">
			<!-- ACK.A.1 - ICSR Batch Number -->
			<targetBatch>
				<id extension="{icsrmessagenumb}" root="{$oidBatchNumber}"/>
			</targetBatch>
			<!-- ACK.A.5 - Batch Validation Error -->
			<xsl:if test="string-length(parsingerrormessage) > 0">
				<acknowledgementDetail>
					<text><xsl:value-of select="parsingerrormessage"/></text>
				</acknowledgementDetail>
			</xsl:if>
		</acknowledgement>
	</xsl:template>
	
</xsl:stylesheet>
