<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade Commons)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)
		
		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<xsl:include href="oids.xsl"/>
	
	<!-- Other Variables used for Special Cases -->
	<xsl:variable name="Decade">800</xsl:variable>
	<xsl:variable name="Year">801</xsl:variable>
	<xsl:variable name="Month">802</xsl:variable>
	<xsl:variable name="Week">803</xsl:variable>
	<xsl:variable name="Day">804</xsl:variable>
	<xsl:variable name="Trimester">810</xsl:variable>
	
	<xsl:template name="getDateFormat">
		<xsl:param name="precision"/>
		
		<xsl:choose>
			<xsl:when test="$precision = 4">602</xsl:when> 	<!-- CCYY -->
			<xsl:when test="$precision = 6">610</xsl:when> 	<!-- CCYYMM -->
			<xsl:when test="$precision = 8">102</xsl:when> 	<!-- CCYYMMDD -->
			<xsl:when test="$precision = 10">202</xsl:when> 	<!-- CCYYMMDDHH -->
			<xsl:when test="$precision = 12">203</xsl:when> 	<!-- CCYYMMDDHHMM -->
			<xsl:when test="$precision = 14">204</xsl:when> 	<!-- CCYYMMDDHHMMSS -->
		</xsl:choose>
	</xsl:template>

	<!-- Date Conversion
		Input:	the element name of the date field
					the date value
					the minimum date precision expected
					the maximum date precision expected
	-->
	<xsl:template name="convertDate">
		<xsl:param name="elementName"/>
		<xsl:param name="date-value"/>
		<xsl:param name="min-format"/>
		<xsl:param name="max-format"/>
		
		<xsl:variable name="before-dot">
			<xsl:choose>
				<xsl:when test="string-length(substring-before($date-value, '.')) > 0"><xsl:value-of select="substring-before($date-value, '.')"/></xsl:when>
				<xsl:otherwise><xsl:value-of select="$date-value"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:variable name="before-tz1">
			<xsl:choose>
				<xsl:when test="string-length(substring-before($date-value, '+')) > 0"><xsl:value-of select="substring-before($date-value, '+')"/></xsl:when>
				<xsl:otherwise><xsl:value-of select="$date-value"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
			<xsl:variable name="before-tz2">
			<xsl:choose>
				<xsl:when test="string-length(substring-before($date-value, '-')) > 0"><xsl:value-of select="substring-before($date-value, '-')"/></xsl:when>
				<xsl:otherwise><xsl:value-of select="$date-value"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:variable name="date">
			<xsl:choose>
				<xsl:when test="string-length($before-dot) &lt;= string-length($before-tz1) and string-length($before-dot) &lt;= string-length($before-tz2)"><xsl:value-of select="$before-dot"/></xsl:when>
				<xsl:when test="string-length($before-tz1) &lt;= string-length($before-dot) and string-length($before-tz1) &lt;= string-length($before-tz2)"><xsl:value-of select="$before-tz1"/></xsl:when>
				<xsl:when test="string-length($before-tz2) &lt;= string-length($before-dot) and string-length($before-tz2) &lt;= string-length($before-tz1)"><xsl:value-of select="$before-tz2"/></xsl:when>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:variable name="precision" select="string-length($date)"/>
		<xsl:variable name="min-precision" select="string-length($min-format)"/>
		<xsl:variable name="max-precision" select="string-length($max-format)"/>

		<xsl:variable name="elementFormatName">
			<xsl:choose>
				<xsl:when test="$elementName='patientlastmenstrualdate'">lastmenstrualdateformat</xsl:when>
				<xsl:otherwise><xsl:value-of select="concat($elementName, 'format')"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		
		<xsl:choose>
			<!-- Same precision is accepted -->
			<xsl:when test="$precision >= $min-precision and $max-precision >= $precision">
				<xsl:element name="{$elementFormatName}">
					<xsl:call-template name="getDateFormat">
						<xsl:with-param name="precision" select="$precision"/>
					</xsl:call-template>
				</xsl:element>
				<xsl:element name="{$elementName}">
					<xsl:value-of select="$date"/>
				</xsl:element>
			</xsl:when>
			<!-- More precision than in R2 - Need to truncate -->
			<xsl:when test="$precision > $max-precision">
				<xsl:element name="{$elementFormatName}">
					<xsl:call-template name="getDateFormat">
						<xsl:with-param name="precision" select="$max-precision"/>
					</xsl:call-template>
				</xsl:element>
				<xsl:element name="{$elementName}">
					<xsl:value-of select="substring($date, 1, $max-precision)"/>
				</xsl:element>
			</xsl:when>
			<!-- Less precision than in R2 - Need to extend with default digits -->
			<xsl:when test="$min-precision > $precision">
				<xsl:element name="{$elementFormatName}">
					<xsl:call-template name="getDateFormat">
						<xsl:with-param name="precision" select="$min-precision"/>
					</xsl:call-template>
				</xsl:element>
				<xsl:element name="{$elementName}">
					<xsl:value-of select="$date"/>
					<xsl:call-template name="extend-date">
						<xsl:with-param name="beg" select="$precision + 1"/>
						<xsl:with-param name="end" select="$min-precision"/>
					</xsl:call-template>
				</xsl:element>
			</xsl:when>
			<xsl:when test="$precision = 0">
				<xsl:element name="{$elementFormatName}"/>
				<xsl:element name="{$elementName}"/>
			</xsl:when>
			<xsl:otherwise>
				TODO : <xsl:value-of select="$precision"/> with <xsl:value-of select="$min-precision"/> - <xsl:value-of select="$max-precision"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- Extend a date with default digits -->
	<xsl:template name="extend-date">
		<xsl:param name="beg"/>
		<xsl:param name="end"/>
		
		<xsl:choose>
			<xsl:when test="$beg = 1">0</xsl:when>		<!-- C -->
			<xsl:when test="$beg = 2">0</xsl:when>		<!-- C -->
			<xsl:when test="$beg = 3">0</xsl:when>		<!-- Y -->
			<xsl:when test="$beg = 4">0</xsl:when>		<!-- Y -->
			<xsl:when test="$beg = 5">0</xsl:when>		<!-- M -->
			<xsl:when test="$beg = 6">1</xsl:when>		<!-- M -->
			<xsl:when test="$beg = 7">0</xsl:when>		<!-- D -->
			<xsl:when test="$beg = 8">1</xsl:when>		<!-- D -->
			<xsl:when test="$beg = 9">0</xsl:when>		<!-- H -->
			<xsl:when test="$beg = 10">0</xsl:when>	<!-- H -->
			<xsl:when test="$beg = 11">0</xsl:when>	<!-- M -->
			<xsl:when test="$beg = 12">0</xsl:when>	<!-- M -->
			<xsl:when test="$beg = 13">0</xsl:when>	<!-- S -->
			<xsl:when test="$beg = 14">0</xsl:when>	<!-- S -->
		</xsl:choose>
		<xsl:if test="$end > $beg">
			<xsl:call-template name="extend-date">
				<xsl:with-param name="beg" select="$beg + 1"/>
				<xsl:with-param name="end" select="$end"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>

	<!--	Code mapping	-->
	<xsl:template name="getMapping">
		<xsl:param name="type"/>
		<xsl:param name="code"/>
		<xsl:choose>
			<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]) = 1">
				<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]/@r2"/>
			</xsl:when>
			<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]) > 1">
				<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]/@r2[1]"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:choose>
					<xsl:when test="$type = 'ROUTE'">050</xsl:when>
					<xsl:otherwise><xsl:value-of select="$code" /></xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<!--	Truncate -->
	<xsl:template name="truncate">
		<xsl:param name="string"/>
		<xsl:param name="string-length"/>
		<xsl:choose>
			<xsl:when test="string-length($string)>$string-length">
				<xsl:value-of select="substring($string, 1, $string-length - 3)"/>
				<xsl:text>...</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$string"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<!--	ID - TEXT mapping functions -->
	<xsl:template name="getText">
		<xsl:param name="id"/>
		<xsl:choose>
			<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-id-text/text[./@id=$id]) = 1">
				<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-id-text/text[./@id=$id]"/>
			</xsl:when>
			<xsl:otherwise><xsl:value-of select="$id" /></xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
</xsl:stylesheet>
