<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - A.3 Part)

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

	<!-- Sender : 
	E2B(R2): element "sender"
	E2B(R3): element "controlActEvent"
	-->
	<xsl:template match="sender">
		<subjectOf1 typeCode="SUBJ">
			<controlActEvent classCode="CACT" moodCode="EVN">
				<author typeCode="AUT">
					<assignedEntity classCode="ASSIGNED">
						<!-- A.3.1	Sender Organization Type -->
						<xsl:choose>
							<xsl:when test="string-length(sendertype) = 0"><code code="6" codeSystem="{$oidSenderType}" codeSystemVersion="{$oidSenderTypeCSV}"/></xsl:when>
							<xsl:otherwise><code code="{sendertype}" codeSystem="{$oidSenderType}" codeSystemVersion="{$oidSenderTypeCSV}"/></xsl:otherwise>
						</xsl:choose>
						<!-- A.3.4.abcd Sender Address -->
						<addr>
							<xsl:call-template name="field-or-mask">
								<xsl:with-param name="element">streetAddressLine</xsl:with-param>
								<xsl:with-param name="value" select="senderstreetaddress"/>
							</xsl:call-template>
							<xsl:call-template name="field-or-mask">
								<xsl:with-param name="element">city</xsl:with-param>
								<xsl:with-param name="value" select="sendercity"/>
							</xsl:call-template>
							<xsl:call-template name="field-or-mask">
								<xsl:with-param name="element">state</xsl:with-param>
								<xsl:with-param name="value" select="senderstate"/>
							</xsl:call-template>
							<xsl:call-template name="field-or-mask">
								<xsl:with-param name="element">postalCode</xsl:with-param>
								<xsl:with-param name="value" select="senderpostcode"/>
							</xsl:call-template>
						</addr>
						<!-- A.3.4.fgh Sender Telephone -->
						<xsl:if test="string-length(sendertel) > 0">
							<telecom>
								<xsl:attribute name="value">
									<xsl:text>tel: </xsl:text>
									<xsl:if test="string-length(sendertelcountrycode) > 0">+<xsl:value-of select="sendertelcountrycode"/><xsl:text> </xsl:text></xsl:if>
									<xsl:value-of select="sendertel"/>
									<xsl:if test="string-length(sendertelextension) > 0"><xsl:text> </xsl:text><xsl:value-of select="sendertelextension"/></xsl:if>
								</xsl:attribute>
							</telecom>
						</xsl:if>
						<!-- A.3.4.ijk Sender Fax -->
						<xsl:if test="string-length(senderfax) > 0">
							<telecom>
								<xsl:attribute name="value">
									<xsl:text>fax: </xsl:text>
									<xsl:if test="string-length(senderfaxcountrycode) > 0">+<xsl:value-of select="senderfaxcountrycode"/><xsl:text> </xsl:text></xsl:if>
									<xsl:value-of select="senderfax"/>
									<xsl:if test="string-length(senderfaxextension) > 0"><xsl:text> </xsl:text><xsl:value-of select="senderfaxextension"/></xsl:if>
								</xsl:attribute>
							</telecom>
						</xsl:if>
						<!-- A.3.4.l Sender Email -->
						<xsl:if test="string-length(senderemailaddress) > 0">
							<telecom value="mailto:{senderemailaddress}"/>
						</xsl:if>
						<assignedPerson classCode="PSN" determinerCode="INSTANCE">
							<!-- A.3.3.bcde Sender Name -->
							<name>
								<xsl:call-template name="field-or-mask">
									<xsl:with-param name="element">prefix</xsl:with-param>
									<xsl:with-param name="value" select="sendertitle"/>
								</xsl:call-template>
								<xsl:call-template name="field-or-mask">
									<xsl:with-param name="element">given</xsl:with-param>
									<xsl:with-param name="value" select="sendergivename"/>
								</xsl:call-template>
								<xsl:call-template name="field-or-mask">
									<xsl:with-param name="element">given</xsl:with-param>
									<xsl:with-param name="value" select="sendermiddlename"/>
								</xsl:call-template>
								<xsl:call-template name="field-or-mask">
									<xsl:with-param name="element">family</xsl:with-param>
									<xsl:with-param name="value" select="senderfamilyname"/>
								</xsl:call-template>
							</name>
							<!-- A.3.4.e Sender Country Code -->
							<xsl:if test="string-length(sendercountrycode) > 0">
								<asLocatedEntity classCode="LOCE">
									<location classCode="COUNTRY" determinerCode="INSTANCE">
										<code code="{sendercountrycode}" codeSystem="{$oidISOCountry}"/>
									</location>
								</asLocatedEntity>
							</xsl:if>
						</assignedPerson>
						<!-- A.3.2 Sender Organization -->
						<!-- A.3.3.a Sender Department -->
						<representedOrganization classCode="ORG" determinerCode="INSTANCE">
							<xsl:call-template name="field-or-mask">
								<xsl:with-param name="element">name</xsl:with-param>
								<xsl:with-param name="value" select="senderdepartment"/>
							</xsl:call-template>
							<assignedEntity classCode="ASSIGNED">
								<representedOrganization classCode="ORG" determinerCode="INSTANCE">
									<xsl:choose>
									<xsl:when test="senderorganization = 'PRIVACY'"><name nullFlavor="MSK"/></xsl:when>
									<xsl:otherwise>
										<xsl:call-template name="field-or-mask">
											<xsl:with-param name="element">name</xsl:with-param>
											<xsl:with-param name="value" select="senderorganization"/>
										</xsl:call-template>
									</xsl:otherwise>
								</xsl:choose>
								</representedOrganization>
							</assignedEntity>
						</representedOrganization>
					</assignedEntity>
				</author>
			</controlActEvent>
		</subjectOf1>
	</xsl:template>
	
</xsl:stylesheet>
