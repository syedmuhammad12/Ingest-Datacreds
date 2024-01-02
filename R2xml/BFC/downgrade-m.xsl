<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - M Part)

		Version:		0.92
		Date:			29/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields
-->
	<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xmlns:fo="http://www.w3.org/1999/XSL/Format" 
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" 
	xmlns:mif="urn:hl7-org:v3/mif"
	exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!-- M.1. ICH ICSR Message Header -->
	<xsl:template match="hl7:MCCI_IN200100UV01">
		<ichicsrmessageheader>
			<messagetype>
				<xsl:choose>
				<xsl:when test="hl7:name/@code = '1' and hl7:name/@codeSystem=$oidMessageType">ichicsr</xsl:when>
				<xsl:when test="hl7:name/@code = '1' and hl7:name/@codeSystem=$oidEUMessageType">backlog</xsl:when>			
				<xsl:when test="hl7:name/@code = '2' and hl7:name/@codeSystem=$oidEUMessageType">masterichicsr</xsl:when>
				<xsl:when test="hl7:name/@code = '4' and hl7:name/@codeSystem=$oidEUMessageType">masterichicsr</xsl:when>
				<xsl:otherwise>ichicsr</xsl:otherwise>
			</xsl:choose>			
			</messagetype>
			<messageformatversion>2.1</messageformatversion>
			<messageformatrelease>2.0</messageformatrelease>
			<messagenumb>
				<xsl:value-of select="hl7:id/@extension"/>
			</messagenumb>
			<messagesenderidentifier>
				<xsl:value-of select="hl7:sender/hl7:device/hl7:id/@extension"/>
			</messagesenderidentifier>
			<messagereceiveridentifier>
				<xsl:value-of select="hl7:receiver/hl7:device/hl7:id/@extension"/>
			</messagereceiveridentifier>
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">messagedate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:creationTime/@value"/>
				<xsl:with-param name="min-format">CCYYMMDDHHMMSS</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDDHHMMSS</xsl:with-param>
			</xsl:call-template>
		</ichicsrmessageheader>
	</xsl:template>
</xsl:stylesheet>
