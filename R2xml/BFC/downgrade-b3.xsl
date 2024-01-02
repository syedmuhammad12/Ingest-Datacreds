<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - B.3 Part)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			18/11/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields, removed MedDRA version being included in Test name field and units from being added to low/high ranges
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!--	B.3. Results of tests and procedures relevant to the investigation of the patient -->
	<xsl:template match="hl7:observation" mode="test">
		<test>
			<xsl:if test="string-length(hl7:effectiveTime/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">testdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<testname>
				<xsl:call-template name="testname" />
			</testname>
			<xsl:choose>
				<xsl:when test="string-length(hl7:interpretationCode/@code) > 0">			<!-- coded value -->
					<testresult>
						<xsl:call-template name="getMapping">
							<xsl:with-param name="type">INTERPRETATION</xsl:with-param>
							<xsl:with-param name="code" select="hl7:interpretationCode/@code"/>
						</xsl:call-template>
					</testresult>
				</xsl:when>
				<xsl:when test="count(hl7:value/hl7:center) = 1">							<!-- single quantity -->
					<testresult><xsl:value-of select="hl7:value/hl7:center/@value"/></testresult>
					<testunit><xsl:value-of select="hl7:value/hl7:center/@unit"/></testunit>
				</xsl:when>
				<xsl:when test="count(hl7:value/hl7:low) = 1"> 								<!-- interval -->
					<xsl:choose>
						<xsl:when test="hl7:value/hl7:low/@nullFlavor='NINF'">			<!-- interval less (or equal) than PQ -->
							<testresult>
								<xsl:text>&lt;</xsl:text>
								<xsl:if test="hl7:value/hl7:high/@inclusive=true()"><xsl:text>=</xsl:text></xsl:if>
								<xsl:value-of select="hl7:value/hl7:high/@value"/>
							</testresult>
							<testunit><xsl:value-of select="hl7:value/hl7:high/@unit"/></testunit>
						</xsl:when>
						<xsl:when test="hl7:value/hl7:high/@nullFlavor='PINF'">			<!-- interval greater (or equal) than PQ -->
							<testresult>
								<xsl:text>&gt;</xsl:text>
								<xsl:if test="hl7:value/hl7:low/@inclusive=true()"><xsl:text>=</xsl:text></xsl:if>
								<xsl:value-of select="hl7:value/hl7:low/@value"/>					
							</testresult>
							<testunit><xsl:value-of select="hl7:value/hl7:low/@unit"/></testunit>
						</xsl:when>
					</xsl:choose>
				</xsl:when>
				<xsl:when test="hl7:value/@xsi:type = 'ED'">									<!-- unstructured -->
					<testresult>
						<xsl:call-template name="truncate">
							<xsl:with-param name="string" select="hl7:value"/>
							<xsl:with-param name="string-length">50</xsl:with-param>
						</xsl:call-template>
					</testresult>
				</xsl:when>
			</xsl:choose>
			<lowtestrange>
				<xsl:value-of select="hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='L']/hl7:value/@value"/>
				<xsl:if test="string-length(hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='L']/hl7:value/@unit) > 0 and hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='L']/hl7:value/@unit != 1">
					<!-- <xsl:text> </xsl:text><xsl:value-of select="hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='L']/hl7:value/@unit"/>-->
				</xsl:if>
			</lowtestrange>
			<hightestrange>
				<xsl:value-of select="hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='H']/hl7:value/@value"/>
				<xsl:if test="string-length(hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='H']/hl7:value/@unit) > 0 and hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='H']/hl7:value/@unit != 1">
					<!-- <xsl:text> </xsl:text><xsl:value-of select="hl7:referenceRange/hl7:observationRange[hl7:interpretationCode/@code='H']/hl7:value/@unit"/>-->
				</xsl:if>
			</hightestrange>
			<moreinformation>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type">YESNO</xsl:with-param>
					<xsl:with-param name="code" select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$MoreInformationAvailable and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
				</xsl:call-template>
			</moreinformation>
		</test>
	</xsl:template>
	
	<!-- B.3.r.c Test name -->
	<xsl:template name="testname">
		<xsl:variable name="testname">
			<xsl:choose>
				<xsl:when test="string-length(hl7:code/@code) > 0">
					<xsl:value-of select="hl7:code/@code"/>
					<!-- <xsl:if test="string-length(hl7:code/@codeSystemVersion) > 0"><xsl:text> </xsl:text>(<xsl:value-of select="hl7:code/@codeSystemVersion"/>)</xsl:if> -->
					<!-- Include above statement if the MedDRA version is needed in the free text field -->
				</xsl:when>
				<xsl:otherwise><xsl:value-of select="hl7:code/hl7:originalText"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:call-template name="truncate">
			<xsl:with-param name="string">
				<xsl:value-of select="$testname"/>
			</xsl:with-param>
			<xsl:with-param name="string-length">100</xsl:with-param>
		</xsl:call-template>
	</xsl:template>
</xsl:stylesheet>
