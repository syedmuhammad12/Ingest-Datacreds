<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade)
		Input : 			ICSR File compliant with E2B(R2)
		Output : 		ICSR File compliant with E2B(R3)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			05/12/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields, improved preservation of known UCUM codes 
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	<xsl:include href="oids.xsl"/>
	
	<!-- Other Variables used for Special Cases -->
	<xsl:variable name="Decade">800</xsl:variable>
	<xsl:variable name="Year">801</xsl:variable>
	<xsl:variable name="Month">802</xsl:variable>
	<xsl:variable name="Week">803</xsl:variable>
	<xsl:variable name="Day">804</xsl:variable>
	<xsl:variable name="Trimester">810</xsl:variable>
	
	<!-- Convert an R2 code into the corresponding R3 code as specificed in the "mapping-codes.xml" file -->
	<xsl:template name="getMapping">
		<xsl:param name="type"/>
		<xsl:param name="code"/>
		
		
		<!-- check length if numeric and add leading zeros if missing  -->
			<xsl:choose>
				<xsl:when test="string-length($code) &lt; 3">
							<xsl:choose>
								<xsl:when test="string(number($code)) != 'NaN'">
										<xsl:if test="string-length($code) = 1">
											<xsl:choose>
												<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = concat('00',$code)]) = 1">
													<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = concat('00',$code)]/@r3"/>
												</xsl:when>
												<xsl:otherwise>{<xsl:value-of select="concat('00',$code)"/>}</xsl:otherwise>
												</xsl:choose>
										</xsl:if>
										<xsl:if test="string-length($code) = 2">
											<xsl:choose>
												<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = concat('0',$code)]) = 1">
													<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = concat('0',$code)]/@r3"/>
												</xsl:when>
												<xsl:otherwise>{<xsl:value-of select="$code"/>}</xsl:otherwise>
											</xsl:choose>
										</xsl:if>
										<xsl:if test="string-length($code) > 2">
											<xsl:choose>
												<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]) = 1">
													<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]/@r3"/>
												</xsl:when>
												<xsl:otherwise>{<xsl:value-of select="$code"/>}</xsl:otherwise>
											</xsl:choose>
										</xsl:if>
								</xsl:when>
								<xsl:otherwise>
									<xsl:choose>
										<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]) = 1">
											<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]/@r3"/>
										</xsl:when>
										<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[text()= $code]) = 1">
											<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[text()= $code]/@r3"/>
										</xsl:when>
										<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]) > 0">
											<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code][1]/@r3"/>
										</xsl:when>
											<!--	<xsl:value-of select="$code"/> -->
										<xsl:otherwise>{<xsl:value-of select="translate($code, ' ', '-')"/>}</xsl:otherwise>
									</xsl:choose>
								</xsl:otherwise>
							</xsl:choose>
					</xsl:when>
				<xsl:otherwise>
					<xsl:choose>
						<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]) = 1">
							<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r2 = $code]/@r3"/>
						</xsl:when>
						<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[text()= $code]) = 1">
							<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[text()= $code]/@r3"/>
						</xsl:when>
						<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code]) > 0">
							<xsl:value-of select="document('mapping-codes.xml')/mapping-codes/mapping-code[./@type=$type]/code[./@r3 = $code][1]/@r3"/>
						</xsl:when>
							<!--	<xsl:value-of select="$code"/> -->
						<xsl:otherwise>{<xsl:value-of select="translate($code, ' ', '-')"/>}</xsl:otherwise>
				</xsl:choose>
				</xsl:otherwise>				
			</xsl:choose>
	</xsl:template>
	
	<!-- Return yes if N8, no otherwise -->
	<xsl:template name="isMeddraCode">
		<xsl:param name="code"/>
		<xsl:choose>
			<xsl:when test="string-length($code) = 8">
				<xsl:choose>
					<xsl:when test="number($code) = $code">
						<xsl:choose>
							<xsl:when test="floor($code) = $code">yes</xsl:when>
							<xsl:otherwise>no</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>no</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:otherwise>no</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
</xsl:stylesheet>
