<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - A.2 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	<!-- Primary Source : 
	E2B(R2): element "primarysource"
	E2B(R3): element "relatedInvestigation"
	-->
	<xsl:template match="primarysource">
		<outboundRelationship typeCode="SPRT">
			<!-- A.2.r.1.5 Primary Source for Regulatory Purposes -->
			<xsl:if test="position() = 1"><priorityNumber value="1"/></xsl:if>
			<relatedInvestigation classCode="INVSTG" moodCode="EVN">
				<code code="{$SourceReport}" codeSystem="{$oidReportRelationCode}"/>
				<subjectOf2 typeCode="SUBJ">
					<controlActEvent classCode="CACT" moodCode="EVN">
						<author typeCode="AUT">
							<assignedEntity classCode="ASSIGNED">
								<!-- A.2.r.1.2.cdef Reporter Address -->
								<addr>
									<xsl:call-template name="field-or-mask">
										<xsl:with-param name="element">streetAddressLine</xsl:with-param>
										<xsl:with-param name="value" select="reporterstreet"/>
									</xsl:call-template>
									<xsl:call-template name="field-or-mask">
										<xsl:with-param name="element">city</xsl:with-param>
										<xsl:with-param name="value" select="reportercity"/>
									</xsl:call-template>
									<xsl:call-template name="field-or-mask">
										<xsl:with-param name="element">state</xsl:with-param>
										<xsl:with-param name="value" select="reporterstate"/>
									</xsl:call-template>
									<xsl:call-template name="field-or-mask">
										<xsl:with-param name="element">postalCode</xsl:with-param>
										<xsl:with-param name="value" select="reporterpostcode"/>
									</xsl:call-template>
								</addr>
								<assignedPerson classCode="PSN" determinerCode="INSTANCE">
									<!-- A.2.r.1.1 Reporter Identifier -->
									<name>
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">prefix</xsl:with-param>
											<xsl:with-param name="value" select="reportertitle"/>
										</xsl:call-template>
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">given</xsl:with-param>
											<xsl:with-param name="value" select="reportergivename"/>
										</xsl:call-template>
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">given</xsl:with-param>
											<xsl:with-param name="value" select="reportermiddlename"/>
										</xsl:call-template>
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">family</xsl:with-param>
											<xsl:with-param name="value" select="reporterfamilyname"/>
										</xsl:call-template>
									</name>
									<!-- A.2.r.1.4 Reporter Qualification -->
									<asQualifiedEntity classCode="QUAL">
										<xsl:choose>
											<xsl:when test="string-length(qualification) > 0"><code code="{qualification}" codeSystem="{$oidQualification}" codeSystemVersion="{$oidQualificationCSV}" /></xsl:when>
											<xsl:otherwise><code nullFlavor="UNK"/></xsl:otherwise>
										</xsl:choose>
									</asQualifiedEntity>
									<!-- A.2.r.1.3 Reporter Country -->
									<xsl:if test="string-length(reportercountry) > 0">
										<asLocatedEntity classCode="LOCE">
											<location determinerCode="INSTANCE" classCode="COUNTRY">
												<code code="{reportercountry}" codeSystem="{$oidISOCountry}"/>
											</location>
										</asLocatedEntity>
									</xsl:if>
									<xsl:if test="position() = 1 and string-length(reportercountry) = 0">
										<xsl:variable name="primreportercountry" select="../primarysourcecountry"/>
										<xsl:if test="string-length($primreportercountry) > 0">
											<asLocatedEntity classCode="LOCE">
												<location determinerCode="INSTANCE" classCode="COUNTRY">
													<code code="{$primreportercountry}" codeSystem="{$oidISOCountry}"/>
												</location>
											</asLocatedEntity>
										</xsl:if>
									</xsl:if>
								</assignedPerson>
								<!-- A.2.r.1.2.ab Reporter Organization -->
								<xsl:if test="string-length(reporterorganization) + string-length(reporterdepartment) > 0">
									<representedOrganization classCode="ORG" determinerCode="INSTANCE">
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">name</xsl:with-param>
											<xsl:with-param name="value" select="reporterdepartment"/>
										</xsl:call-template>
										<xsl:if test="string-length(reporterorganization) > 0">
											<assignedEntity classCode="ASSIGNED">
												<representedOrganization classCode="ORG" determinerCode="INSTANCE">
													<xsl:call-template name="field-or-mask">
														<xsl:with-param name="element">name</xsl:with-param>
														<xsl:with-param name="value" select="reporterorganization"/>
													</xsl:call-template>
												</representedOrganization>
											</assignedEntity>
										</xsl:if>
									</representedOrganization>
								</xsl:if>
							</assignedEntity>
						</author>
					</controlActEvent>
				</subjectOf2>
			</relatedInvestigation>
		</outboundRelationship>
	</xsl:template>

	<!-- display content of a field, unless it is masked -->
	<xsl:template name="field-or-mask">
		<xsl:param name="element"/>
		<xsl:param name="value"/>
		
		<xsl:if test="string-length($value) > 0">
			<xsl:element name="{$element}">
				<xsl:choose>
					<xsl:when test="$value = 'PRIVACY'"><xsl:attribute name="nullFlavor">MSK</xsl:attribute></xsl:when>
					<xsl:when test="$value = 'UNKNOWN'"><xsl:attribute name="nullFlavor">UNK</xsl:attribute></xsl:when>
					<xsl:otherwise><xsl:value-of select="$value"/></xsl:otherwise>
				</xsl:choose>
			</xsl:element>
		</xsl:if>
	</xsl:template>
	
</xsl:stylesheet>
