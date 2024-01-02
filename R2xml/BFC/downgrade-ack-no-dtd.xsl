<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - ACK)
		Input : 			ICSR ACK File compliant with E2B(R3)
		Output : 		ICSR ACK File compliant with E2B(R2)

		Version:		0.7
		Date:			04/05/2011
		Status:		Draft
		Author:		Laurent DESQUEPER (EU)

-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<xsl:include href="downgrade.xsl"/>
		
	<xsl:output indent="yes" method="xml" omit-xml-declaration="no" encoding="utf-8"/>

<!-- ICH ICSR ACK -->
	<xsl:template match="/">
		<ichicsrack lang="en">
			<xsl:apply-templates select="hl7:MCCI_IN200101UV01" mode="header"/>
			<xsl:apply-templates select="hl7:MCCI_IN200101UV01" mode="message"/>
		</ichicsrack>
	</xsl:template>

	<!-- M - ACK Message Header -->
	<xsl:template match="hl7:MCCI_IN200101UV01" mode="header">
		<ichicsrmessageheader>
			<!-- M.1.1 - Message Type -->
			<messagetype>ichicsrack</messagetype>
			<!-- M.1.2 - Message Format Version -->
			<messageformatversion>2.1</messageformatversion>
			<!-- M.1.3 - Message Release Version -->
			<messageformatrelease>1.0</messageformatrelease>
			<!-- M.1.4 - Message Number -->
			<messagenumb><xsl:value-of select="hl7:id/@extension"/></messagenumb>
			<!-- M.1.5 - Message Sender Identifier -->
			<messagesenderidentifier><xsl:value-of select="hl7:sender/hl7:device/hl7:id/@extension"/></messagesenderidentifier>
			<!-- M.1.6 - Message Receiver Identifier -->
			<messagereceiveridentifier><xsl:value-of select="hl7:receiver/hl7:device/hl7:id/@extension"/></messagereceiveridentifier>
			<!-- M.1.7 - Message Date -->
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">messagedate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:creationTime/@value"/>
				<xsl:with-param name="min-format">CCYYMMDDHHMMSS</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDDHHMMSS</xsl:with-param>
			</xsl:call-template>
		</ichicsrmessageheader>
	</xsl:template>
	
	<!-- A - Message Acknowledgment -->
	<xsl:template match="hl7:MCCI_IN200101UV01" mode="message">
		<acknowledgment>
			<messageacknowledgment>
				<!-- A.1.1 - ICSR Message Number -->
				<icsrmessagenumb><xsl:value-of select="hl7:acknowledgement/hl7:targetBatch/hl7:id/@extension"/></icsrmessagenumb>
				<!-- A.1.2 - Local Message Number -->
				<localmessagenumb><xsl:value-of select="hl7:attentionLine[hl7:keyWordText/@code = $AckLocalMessageNumber and hl7:keyWordText/@codeSystem=$oidAttentionLineCode]/hl7:value/@extension"/></localmessagenumb>
				<!-- A.1.3 - ICSR Message Sender ID -->
				<icsrmessagesenderidentifier><xsl:value-of select="hl7:MCCI_IN000002UV01[1]/hl7:sender/hl7:device/hl7:id/@extension"/></icsrmessagesenderidentifier>
				<!-- A.1.4 - ICSR Message Receiver ID -->
				<icsrmessagereceiveridentifier><xsl:value-of select="hl7:MCCI_IN000002UV01[1]/hl7:receiver/hl7:device/hl7:id/@extension"/></icsrmessagereceiveridentifier>
				<!-- A.1.5 - ICSR Message Date -->
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">icsrmessagedate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:attentionLine[hl7:keyWordText/@code = $DateOfIcsrBatchTransmission and hl7:keyWordText/@codeSystem=$oidAttentionLineCode]/hl7:value/@value"/>
					<xsl:with-param name="min-format">CCYYMMDDHHMMSS</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDDHHMMSS</xsl:with-param>
				</xsl:call-template>
				<!-- A.1.6 - Transmission ACK Code -->
				<xsl:variable name="ackCode" select="hl7:acknowledgement/@typeCode"/>
				<transmissionacknowledgmentcode>
					<xsl:choose>
						<xsl:when test="$ackCode = 'AA'">01</xsl:when>
						<xsl:when test="$ackCode = 'AE'">02</xsl:when>
						<xsl:otherwise>03</xsl:otherwise>
					</xsl:choose>
				</transmissionacknowledgmentcode>
				<!-- A.1.7 - Parsing Error Message -->
				<parsingerrormessage><xsl:value-of select="hl7:acknowledgement/hl7:acknowledgementDetail/hl7:text"/></parsingerrormessage>
			</messageacknowledgment>
			<!-- B - Report Acknowledgment -->
			<xsl:apply-templates select="hl7:MCCI_IN000002UV01"/>
		</acknowledgment>
	</xsl:template>
	
	<!-- B - Report Acknowledgment -->
	<xsl:template match="hl7:MCCI_IN000002UV01">
		<reportacknowledgment>
			<!-- B.1.1 - Safety Report ID -->
			<safetyreportid><xsl:value-of select="hl7:acknowledgement/hl7:targetMessage/hl7:id/@extension"/></safetyreportid>
			<!-- B.1.3 - Local Report Number -->
			<localreportnumb><xsl:value-of select="hl7:id/@extension"/></localreportnumb>
			<!-- B.1.7 - Receipt Date -->
			<xsl:if test="string-length(hl7:attentionLine[hl7:keyWordText/@code = $receiptDate]/hl7:value/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">receiptdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:attentionLine[hl7:keyWordText/@code = $receiptDate]/hl7:value/@value"/>
					<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<!-- B.1.8 - ACK Code for Report -->
			<xsl:variable name="ackCode" select="hl7:acknowledgement/@typeCode"/>
			<reportacknowledgmentcode>
				<xsl:choose>
					<xsl:when test="$ackCode = 'CA'">01</xsl:when>
					<xsl:when test="$ackCode = 'CR'">02</xsl:when>
				</xsl:choose>
			</reportacknowledgmentcode>
			<!-- B.1.9 - Error Message or Comment -->
			<errormessagecomment><xsl:value-of select="hl7:acknowledgement/hl7:acknowledgementDetail/hl7:text"/></errormessagecomment>
		</reportacknowledgment>
	</xsl:template>
</xsl:stylesheet>
