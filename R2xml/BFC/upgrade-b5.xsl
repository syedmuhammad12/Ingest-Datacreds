<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - B.5 Part)

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

	<!-- Narrative Include Clinical : 
	E2B(R2): element "narrativeincludeclinical"
	E2B(R3): element "investigationEvent"
	-->
	<xsl:template match="narrativeincludeclinical">
		<xsl:if test="string-length(.) > 0">
			<text mediaType="text/plain">
				<xsl:value-of select="."/>
			</text>
		</xsl:if>	
	</xsl:template>
	
	<!-- Summary : 
	E2B(R2): element "summary"
	E2B(R3): element "investigationEvent"
	-->
	<xsl:template match="summary">
		<!-- B.5.2 Reporter's Comments -->
		<xsl:if test="string-length(reportercomment) > 0">
			<component1 typeCode="COMP">
				<observationEvent moodCode="EVN" classCode="OBS">
					<code code="{$Comment}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="ED" mediaType="text/plain"><xsl:value-of select="reportercomment"/></value>
					<author typeCode="AUT">
						<assignedEntity classCode="ASSIGNED">
							<code code="{$SourceReporter}" codeSystem="{$oidAssignedEntityRoleCode}"/>
						</assignedEntity>
					</author>
				</observationEvent>
			</component1>
		</xsl:if>
		<!-- B.5.3.r Sender's diagnosis/syndrome code -->
		<xsl:if test="string-length(senderdiagnosis) > 0">
			<component1 typeCode="COMP">
				<observationEvent moodCode="EVN" classCode="OBS">
					<code code="{$Diagnosis}" codeSystem="{$oidObservationCode}"/>
					<xsl:variable name="isMeddraCode">
						<xsl:call-template name="isMeddraCode">
							<xsl:with-param name="code" select="senderdiagnosis"/>
						</xsl:call-template>
					</xsl:variable>
					<xsl:choose>
						<xsl:when test="$isMeddraCode = 'yes'">
							<value xsi:type="CE" code="{senderdiagnosis}">
								<xsl:if test="string-length(senderdiagnosismeddraversion) > 0">
									<xsl:attribute name="codeSystem"><xsl:value-of select="$oidMedDRA"/></xsl:attribute>
									<xsl:attribute name="codeSystemVersion"><xsl:value-of select="senderdiagnosismeddraversion"/></xsl:attribute>
								</xsl:if>
							</value>
						</xsl:when>
						<xsl:otherwise>
							<value xsi:type="CE" >
								<originalText>
									<xsl:value-of select="senderdiagnosis"/>
									<xsl:if test="string-length(senderdiagnosismeddraversion) > 0"> (<xsl:value-of select="senderdiagnosismeddraversion"/>)</xsl:if>
								</originalText>
							</value>
						</xsl:otherwise>
					</xsl:choose>
					<author typeCode="AUT">
						<assignedEntity classCode="ASSIGNED">
							<code code="{$Sender}" codeSystem="{$oidAssignedEntityRoleCode}"/>
						</assignedEntity>
					</author>
				</observationEvent>
			</component1>
		</xsl:if>
		<!-- B.5.4 Sender's Comments -->
		<xsl:if test="string-length(sendercomment) > 0">
			<component1 typeCode="COMP">
				<observationEvent moodCode="EVN" classCode="OBS">
					<code code="{$Comment}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="ED" mediaType="text/plain"><xsl:value-of select="sendercomment"/></value>
					<author typeCode="AUT">
						<assignedEntity classCode="ASSIGNED">
							<code code="{$Sender}" codeSystem="{$oidAssignedEntityRoleCode}"/>
						</assignedEntity>
					</author>
				</observationEvent>
			</component1>
		</xsl:if>
	</xsl:template>
	
</xsl:stylesheet>
