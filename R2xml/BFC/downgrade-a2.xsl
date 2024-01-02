<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - A.2 Part, including A.5)
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
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif" exclude-result-prefixes="hl7 xsi xsl fo mif">
	<!-- A.2 Primary sources -->
	<xsl:template match="hl7:assignedEntity" mode="primary-source">
		<primarysource>
			<reportertitle>
				<xsl:apply-templates select="hl7:assignedPerson/hl7:name/hl7:prefix" mode="field-or-mask"/>
			</reportertitle>
			<reportergivename>
				<xsl:apply-templates select="hl7:assignedPerson/hl7:name/hl7:given[1]" mode="field-or-mask">
					<xsl:with-param name="size">35</xsl:with-param>
				</xsl:apply-templates>
			</reportergivename>
			<reportermiddlename>
				<xsl:apply-templates select="hl7:assignedPerson/hl7:name/hl7:given[2]" mode="field-or-mask">
					<xsl:with-param name="size">15</xsl:with-param>
				</xsl:apply-templates>
			</reportermiddlename>
			<reporterfamilyname>
				<xsl:apply-templates select="hl7:assignedPerson/hl7:name/hl7:family" mode="field-or-mask">
					<xsl:with-param name="size">50</xsl:with-param>
				</xsl:apply-templates>
			</reporterfamilyname>
			<reporterorganization>
				<xsl:apply-templates select="hl7:representedOrganization/hl7:assignedEntity/hl7:representedOrganization/hl7:name" mode="field-or-mask"/>	
			</reporterorganization>
			<reporterdepartment>
				<xsl:apply-templates select="hl7:representedOrganization/hl7:name" mode="field-or-mask"/>
			</reporterdepartment>
			<reporterstreet>
				<xsl:apply-templates select="hl7:addr/hl7:streetAddressLine" mode="field-or-mask"/>
			</reporterstreet>
			<reportercity>
				<xsl:apply-templates select="hl7:addr/hl7:city" mode="field-or-mask"/>
			</reportercity>
			<reporterstate>
				<xsl:apply-templates select="hl7:addr/hl7:state" mode="field-or-mask"/>
			</reporterstate>
			<reporterpostcode>
				<xsl:apply-templates select="hl7:addr/hl7:postalCode" mode="field-or-mask"/>
			</reporterpostcode>
			<reportercountry>
				<xsl:value-of select="hl7:assignedPerson/hl7:asLocatedEntity/hl7:location/hl7:code/@code"/>
			</reportercountry>
			<qualification>
				<xsl:value-of select="hl7:assignedPerson/hl7:asQualifiedEntity/hl7:code/@code"/>
			</qualification>
			<xsl:if test="position()=1">
				<!-- A.4.3. Literature reference(s) -->
				<literaturereference>
					<xsl:variable name="lit-ref">
						<xsl:for-each select="../../../../../../hl7:reference/hl7:document/hl7:bibliographicDesignationText[string-length(.) > 0]">
							<xsl:value-of select="."/>
							<xsl:if test="not (position()=last())">
								<xsl:text>; </xsl:text>
							</xsl:if>
						</xsl:for-each>
					</xsl:variable>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string" select="$lit-ref"/>
						<xsl:with-param name="string-length">500</xsl:with-param>
					</xsl:call-template>
				</literaturereference>
				<xsl:apply-templates select="../../../../../../hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf1/hl7:researchStudy" mode="StudyIdentification"/>
			</xsl:if>
		</primarysource>
	</xsl:template>
	<!--	A.5. Study identification -->
	<xsl:template match="hl7:researchStudy" mode="StudyIdentification">
		<xsl:call-template name="StudyName">
			<xsl:with-param name="Length">100</xsl:with-param>
		</xsl:call-template>
		<sponsorstudynumb>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string">
					<xsl:value-of select="hl7:id/@extension"/>
				</xsl:with-param>
				<xsl:with-param name="string-length">35</xsl:with-param>
			</xsl:call-template>
		</sponsorstudynumb>
		<observestudytype>
			<xsl:value-of select="hl7:code/@code"/>
		</observestudytype>
	</xsl:template>
	<!-- A.5.2 Study name -->
	<xsl:template name="StudyName">
		<xsl:param name="NarrativeText"/>
		<xsl:param name="Length">0</xsl:param>
		<xsl:variable name="ContentString">
			<!-- preconcat A.5.1.r.2 (use seperator #) -->
			<xsl:for-each select="hl7:authorization/hl7:studyRegistration">
				<xsl:choose>
					<xsl:when test="hl7:author/hl7:territorialAuthority/hl7:governingPlace/hl7:code/@code='EU'">
						<xsl:value-of select="hl7:id/@extension"/>
						<xsl:text>#</xsl:text>
					</xsl:when>
					<xsl:when test="hl7:author/hl7:territorialAuthority/hl7:governingPlace/hl7:code/@code!='EU'">
						<xsl:value-of select="hl7:author/hl7:territorialAuthority/hl7:governingPlace/hl7:code/@code"/>
						<xsl:text>-</xsl:text>
				<xsl:choose>
					<xsl:when test="hl7:id/@extension">
						<xsl:value-of select="hl7:id/@extension"/>
					</xsl:when>
					<xsl:otherwise>UNKNOWN</xsl:otherwise>
				</xsl:choose>
				<xsl:text>: </xsl:text>
					</xsl:when>
				</xsl:choose>
			</xsl:for-each>
			<xsl:choose>
				<xsl:when test="count(hl7:title/@nullFlavor) = 0">
					<xsl:value-of select="hl7:title"/>
				</xsl:when>
				<xsl:otherwise>UNKNOWN</xsl:otherwise>
			</xsl:choose>
			<xsl:if test="position() != last()">
				<xsl:text>; </xsl:text>
			</xsl:if>
		</xsl:variable>
		<xsl:choose>
			<xsl:when test="string-length($NarrativeText) = 0">
				<studyname>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string">
							<xsl:value-of select="$ContentString"/>
						</xsl:with-param>
						<xsl:with-param name="string-length">
							<xsl:value-of select="$Length"/>
						</xsl:with-param>
					</xsl:call-template>
				</studyname>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="string-length($ContentString)>$Length">
					<xsl:value-of select="$NarrativeText"/>
					<xsl:value-of select="$ContentString"/>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template match="*" mode="field-or-mask">
		<xsl:param name="size">0</xsl:param>
		<xsl:choose>
			<xsl:when test="@nullFlavor = 'MSK'">PRIVACY</xsl:when>
			<xsl:when test="@nullFlavor = 'UNK'">UNKNOWN</xsl:when>
			<xsl:when test="@nullFlavor = 'ASKU'">UNKNOWN</xsl:when>
			<xsl:when test="@nullFlavor = 'NASK'">UNKNOWN</xsl:when>
			<xsl:otherwise>
				<xsl:if test="$size = 0">
					<xsl:value-of select="."/>
				</xsl:if>
				<xsl:if test="$size > 0">
					<xsl:call-template name="truncate">
						<xsl:with-param name="string" select="."/>
						<xsl:with-param name="string-length" select="$size"/>
					</xsl:call-template>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>
