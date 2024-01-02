<?xml version="1.0" encoding="UTF-8"?>
<!--
		UT File for ICSR Downgrade R3 -> R2
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  
	xmlns:ut="urn:ich"
	exclude-result-prefixes="hl7 xsi xsl fo mif ut">
	
	<xsl:include href="downgrade.xsl"/>
	<xsl:include href="downgrade-m.xsl"/>
	<xsl:include href="downgrade-a1.xsl"/>
	<xsl:include href="downgrade-a2.xsl"/>
	<xsl:include href="downgrade-a3.xsl"/>
	<xsl:include href="downgrade-b1.xsl"/>
	<xsl:include href="downgrade-b2.xsl"/>
	<xsl:include href="downgrade-b3.xsl"/>
	<xsl:include href="downgrade-b4.xsl"/>
	<xsl:include href="downgrade-b5.xsl"/>

	<!-- Unit Test Data for DAT mapping -->
	<ut:cases name="DAT" desc="conversion of dates">
		<case desc="same format CCYY">
			<date-value>2011</date-value>
			<min-format>CCYY</min-format>
			<max-format>CCYY</max-format>
			<result>602 - 2011</result>
		</case>
		<case desc="same format CCYYMM">
			<date-value>201106</date-value>
			<min-format>CCYYMM</min-format>
			<max-format>CCYYMM</max-format>
			<result>610 - 201106</result>
		</case>
		<case desc="same format CCYYMMDD">
			<date-value>20110615</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="same format CCYYMMDDhh">
			<date-value>2011061510</date-value>
			<min-format>CCYYMMDDHH</min-format>
			<max-format>CCYYMMDDHH</max-format>
			<result>202 - 2011061510</result>
		</case>
		<case desc="same format CCYYMMDDhhmm">
			<date-value>201106151028</date-value>
			<min-format>CCYYMMDDHHMM</min-format>
			<max-format>CCYYMMDDHHMM</max-format>
			<result>203 - 201106151028</result>
		</case>
		<case desc="same format CCYYMMDDhhmmss">
			<date-value>20110615102845</date-value>
			<min-format>CCYYMMDDHHMMSS</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>204 - 20110615102845</result>
		</case>
		<case desc="same format supported in list CCYY">
			<date-value>2011</date-value>
			<min-format>CCYY</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>602 - 2011</result>
		</case>
		<case desc="same format supported in list CCYYMM">
			<date-value>201106</date-value>
			<min-format>CCYY</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>610 - 201106</result>
		</case>
		<case desc="same format supported in list CCYYMMDD">
			<date-value>20110615</date-value>
			<min-format>CCYY</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="same format supported in list CCYYMMDD">
			<date-value>20110615</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="same format supported in list CCYYMMDDhh">
			<date-value>2011061510</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>202 - 2011061510</result>
		</case>
		<case desc="same format supported in list CCYYMMDDhhmm">
			<date-value>201106151028</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>203 - 201106151028</result>
		</case>
		<case desc="same format supported in list CCYYMMDDhhmmss">
			<date-value>20110615102845</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>204 - 20110615102845</result>
		</case>
		<case desc="conversion to less precision">
			<date-value>20110615102845</date-value>
			<min-format>CCYY</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="conversion to more precision CCYYMMDD">
			<date-value>2011</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>102 - 20110101</result>
		</case>
		<case desc="conversion to more precision CCYYMMDDhhmm">
			<date-value>20110615</date-value>
			<min-format>CCYYMMDDHHMM</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>203 - 201106150000</result>
		</case>
		<case desc="conversion of date with ms; format SS">
			<date-value>20110615102845.1234</date-value>
			<min-format>CCYYMMDDHHMMSS</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>204 - 20110615102845</result>
		</case>
		<case desc="conversion of date with ms; format DD">
			<date-value>20110615102845.1234</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="conversion of date with tz+; format DD">
			<date-value>20110615102845+06</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="conversion of date with tz-; format SS; more precision">
			<date-value>201106151028-06</date-value>
			<min-format>CCYYMMDDHHMMSS</min-format>
			<max-format>CCYYMMDDHHMMSS</max-format>
			<result>20110615102800</result>
		</case>
		<case desc="conversion of date with ms and tz-; format DD">
			<date-value>20110615102845.1234-06</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
		<case desc="conversion of date with long tz+; format DD">
			<date-value>20110615102845+0630</date-value>
			<min-format>CCYYMMDD</min-format>
			<max-format>CCYYMMDD</max-format>
			<result>102 - 20110615</result>
		</case>
	</ut:cases>
	<!-- Unit Test Data for COD mapping -->
	<ut:cases name="COD" desc="conversion of codes">
		<case desc="UCUM code - kg">
			<code-type>UCUM</code-type>
			<code-value>kg</code-value>
			<result>001</result>
		</case>
		<case desc="UCUM code - L">
			<code-type>UCUM</code-type>
			<code-value>L</code-value>
			<result>011</result>
		</case>
		<case desc="UCUM code - y">
			<code-type>UCUM</code-type>
			<code-value>a</code-value>
			<result>801</result>
		</case>
	</ut:cases>
	<ut:cases name="MEDDRA" desc="conversion of MedDRA">
		<case desc="MedDRA code - N8">
			<code-value>12345678</code-value>
			<result>ok</result>
		</case>
		<case desc="MedDRA code - N6">
			<code-value>123456</code-value>
			<result>nok</result>
		</case>
		<case desc="MedDRA code - N10">
			<code-value>1234567890</code-value>
			<result>nok</result>
		</case>
		<case desc="MedDRA code - N8 + dot">
			<code-value>123456.8</code-value>
			<result>nok</result>
		</case>
		<case desc="MedDRA code - AN8">
			<code-value>1b3d5f78</code-value>
			<result>nok</result>
		</case>
		<case desc="MedDRA code - A8">
			<code-value>abcdefgh</code-value>
			<result>nok</result>
		</case>
	</ut:cases>
	
	<xsl:output indent="yes" method="xml" omit-xml-declaration="no" encoding="utf-8"/>
	<xsl:strip-space elements="*"/>
	
	<xsl:template match="/">
		<unit-testing>
			<!--xsl:apply-templates select="//ut:cases[@name='DAT']/case" mode="DAT"/-->
			<!--xsl:apply-templates select="//ut:cases[@name='COD']/case" mode="COD"/-->
			<xsl:apply-templates select="//ut:cases[@name='MEDDRA']/case" mode="MEDDRA"/>
		</unit-testing>
	</xsl:template>
	
	<!-- Unit Test Case for DAT mapping -->
	<xsl:template match="case" mode="DAT">
		<case>
			<xsl:attribute name="desc"><xsl:value-of select="@desc"/></xsl:attribute>
			<input-date><xsl:value-of select="date-value"/></input-date>
			<input-min><xsl:value-of select="min-format"/></input-min>
			<input-max><xsl:value-of select="max-format"/></input-max>
			<exp-result><xsl:value-of select="result"/></exp-result>
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">elementName</xsl:with-param>
				<xsl:with-param name="date-value" select="date-value"/>
				<xsl:with-param name="min-format" select="min-format"/>
				<xsl:with-param name="max-format" select="max-format"/>
			</xsl:call-template>
		</case>
	</xsl:template>
	
	<!-- Unit Test Case for COD mapping -->
	<xsl:template match="case" mode="COD">
		<case>
			<xsl:attribute name="desc"><xsl:value-of select="@desc"/></xsl:attribute>
			<input-date><xsl:value-of select="code-value"/></input-date>
			<exp-result><xsl:value-of select="result"/></exp-result>
			<value>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type" select="code-type"/>
					<xsl:with-param name="code" select="code-value"/>
				</xsl:call-template>
			</value>
		</case>
	</xsl:template>

	<!-- Unit Test Case for MedDRA mapping -->
	<xsl:template match="case" mode="MEDDRA">
		<case>
			<xsl:attribute name="desc"><xsl:value-of select="@desc"/></xsl:attribute>
			<input-date><xsl:value-of select="code-value"/></input-date>
			<exp-result><xsl:value-of select="result"/></exp-result>
			<value>
				<xsl:choose>
					<xsl:when test="string-length(code-value) = 8">														<!-- length must be 8 -->
						<xsl:choose>
							<xsl:when test="number(code-value) = code-value">										<!-- content must be numeric -->
								<xsl:choose>
									<xsl:when test="floor(code-value) = code-value">ok</xsl:when>			<!-- content must be integer -->
									<xsl:otherwise>nok</xsl:otherwise>
								</xsl:choose>
							</xsl:when>
							<xsl:otherwise>nok</xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise>nok</xsl:otherwise>
				</xsl:choose>
			</value>
		</case>
	</xsl:template>

</xsl:stylesheet>
