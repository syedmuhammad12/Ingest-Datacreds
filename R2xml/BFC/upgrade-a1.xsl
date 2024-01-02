<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - A1 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			25/11/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields, bug fix
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	
	<xsl:include href="upgrade-a2.xsl"/>
	<xsl:include href="upgrade-a3.xsl"/>
	<xsl:include href="upgrade-a4.xsl"/>
	<xsl:include href="upgrade-b1.xsl"/>
	<xsl:include href="upgrade-b5.xsl"/>

	<!-- Safety Report (date of transmission) : 
	E2B(R2): element "transmissiondate" inside "safetyreport"
	E2B(R3): element "controlActProcess"
	-->
	<xsl:template match="transmissiondate">
		<xsl:variable name="version-number" select="../safetyreportversion"/>
		<xsl:choose>
			<xsl:when test="string-length($version-number) = 0"><effectiveTime value="{.}"/></xsl:when>
			<xsl:when test="string-length($version-number) = 1"><effectiveTime value="{.}00000{$version-number}"/></xsl:when>
			<xsl:when test="string-length($version-number) = 2"><effectiveTime value="{.}0000{$version-number}"/></xsl:when>
			<xsl:otherwise><effectiveTime value="{.}"/></xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<!-- Safety Report (main) : 
	E2B(R2): element "safetyreport" inside "ichicsr"
	E2B(R3): element "investigationEvent"
	-->
	<xsl:template match="safetyreport" mode="main">
		<subject typeCode="SUBJ">
			<investigationEvent classCode="INVSTG" moodCode="EVN">
				<!-- A.1.0.1 - Sender’s (Case) Safety Report Unique Identifier  -->
				<id root="{$oidSendersReportNamespace}" extension="{safetyreportid}"/>
				<!-- A.1.10.1 - Worldwide Unique Case Identification Number - Rule STR-03  -->
				<xsl:choose>
					<xsl:when test="string-length(authoritynumb) > 0">
						<id root="{$oidWorldWideCaseID}" extension="{authoritynumb}"/>
					</xsl:when>
					<xsl:when test="string-length(companynumb) > 0">
						<id root="{$oidWorldWideCaseID}" extension="{companynumb}"/>
					</xsl:when>
					<xsl:otherwise>
						<id root="{$oidWorldWideCaseID}" nullFlavor="UNK"/>
					</xsl:otherwise>
				</xsl:choose>
				<code code="PAT_ADV_EVNT" codeSystem="2.16.840.1.113883.5.4"/>
				<!-- B.5.1 Case Narrative -->
				<xsl:apply-templates select="patient/summary/narrativeincludeclinical"/>
				<statusCode code="active"/>
				<!-- A.1.6 - Date Report Was First Received from Source -->
				<xsl:if test="string-length(receivedate) > 0">
					<effectiveTime>
						<low value="{receivedate}"/>
					</effectiveTime>
				</xsl:if>
				<!-- A.1.7 - Date of Most Recent Information for this Case -->
				<xsl:if test="string-length(receiptdate) > 0">
					<availabilityTime value="{receiptdate}"/>
				</xsl:if>
				<!-- A.1.8.1.r Document Held by Sender -->
				<xsl:apply-templates select="documentlist"/>
				<!-- BFC: Document Added to State Conversion -->
				<reference typeCode="REFR">
					<document classCode="DOC" moodCode="EVN">
						<code code="{$documentsHeldBySender}" codeSystem="{$oidichreferencesource}" displayName="documentsHeldBySender"/>
						<title>Source of this Case Safety Report in E2B(R2) Format</title>
					</document>
				</reference>
				<!-- A.4.r Literature References -->
				<xsl:apply-templates select="primarysource/literaturereference"/>
				<!-- B.1.x - Patient -->
				<xsl:apply-templates select="patient" mode="identification"/>
				<!-- A.1.8.1 - Are Additional Documents Available? -->
				<component typeCode="COMP">
					<observationEvent classCode="OBS" moodCode="EVN">
						<code code="{$AdditionalDocumentsAvailable}" codeSystem="{$oidObservationCode}" displayName="additionalDocumentsAvailable"/>
						<value xsi:type="BL" value="true"/>
					</observationEvent>
				</component>
				<!-- A.1.9 - Does this Case Fulfil the Local Criteria for an Expedited Report? -->
				<xsl:call-template name="fulfillexpeditecriteria"/>
				<!-- A.1.10.2 First Sender of this Case -->
				<xsl:if test="string-length(authoritynumb) + string-length(companynumb) > 0">
					<outboundRelationship typeCode="SPRT">
						<relatedInvestigation classCode="INVSTG" moodCode="EVN">
							<code code="{$InitialReport}" codeSystem="{$oidReportRelationCode}"/>
							<subjectOf2 typeCode="SUBJ">
								<controlActEvent classCode="CACT" moodCode="EVN">
									<author typeCode="AUT">
										<assignedEntity classCode="ASSIGNED">
											<xsl:choose>
												<xsl:when test="string-length(authoritynumb) > 0">
													<code code="1" codeSystem="{$oidFirstSender}" codeSystemVersion="{$oidFirstSenderCSV}" />
												</xsl:when>
												<xsl:otherwise>
													<code code="2" codeSystem="{$oidFirstSender}"  codeSystemVersion="{$oidFirstSenderCSV}"/>
												</xsl:otherwise>
											</xsl:choose>
										</assignedEntity>
									</author>
								</controlActEvent>
							</subjectOf2>
						</relatedInvestigation>
					</outboundRelationship>
				</xsl:if>
				<!-- A.1.12.r Linked Reports -->
				<xsl:apply-templates select="linkedreport"/>
				<!-- A.2.r Primary Sources -->
				<xsl:apply-templates select="primarysource"/>
				<!-- A.3 Sender -->
				<xsl:apply-templates select="sender"/>
				<!-- A.1.11 Report Duplicate -->
				<xsl:apply-templates select="reportduplicate"/>
				<!-- A.1.4 - Type of Report -->
				<xsl:if test="string-length(reporttype) > 0">
					<subjectOf2 typeCode="SUBJ">
						<investigationCharacteristic classCode="OBS" moodCode="EVN">
							<code code="{$ReportType}" codeSystem="{$oidReportCharacterizationCode}" />
							<value xsi:type="CE" code="{reporttype}" codeSystem="{$oidReportType}" codeSystemVersion="{$oidReportTypeCSV}"/>
						</investigationCharacteristic>
					</subjectOf2>
				</xsl:if>
				<!-- A.1.11 - Other Case Identifiers in Previous Transmissions -->
				<subjectOf2 typeCode="SUBJ">
					<investigationCharacteristic classCode="OBS" moodCode="EVN">
						<code code="{$OtherCaseIDs}" codeSystem="{$oidReportCharacterizationCode}"/>
						<xsl:choose>
							<xsl:when test="duplicate = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</investigationCharacteristic>
				</subjectOf2>
				<!-- A.1.13 Report Nullification / Amendment -->
				<xsl:if test="casenullification = 1">
					<subjectOf2 typeCode="SUBJ">
						<investigationCharacteristic classCode="OBS" moodCode="EVN">
							<code code="{$NullificationAmendmentCode}" codeSystem="{$oidReportCharacterizationCode}"/>
							<value xsi:type="CE" code="1" codeSystem="{$oidNullificationAmendment}" codeSystemVersion="{$oidNullificationAmendment}"/>
						</investigationCharacteristic>
					</subjectOf2>
				</xsl:if>
				<!-- A.1.13.1 Reason for Nullification / Amendment -->
				<xsl:if test="nullificationreason">
					<subjectOf2 typeCode="SUBJ">
						<investigationCharacteristic classCode="OBS" moodCode="EVN">
							<code code="{$NullificationAmendmentReason}" codeSystem="{$oidReportCharacterizationCode}"/>
							<value xsi:type="CE">
								<originalText mediaType="text/plain"><xsl:value-of select="nullificationreason"/></originalText>
							</value>
						</investigationCharacteristic>
					</subjectOf2>
				</xsl:if>
			</investigationEvent>
		</subject>
	</xsl:template>
	
	<!-- Document List : 
	E2B(R2): element "documentlist" inside "safetyreport"
	E2B(R3): element "reference"
	-->
	<xsl:template match="documentlist">
		<!-- A.1.8.1.r.1 - Documents Held by Sender -->
		<xsl:if test="string-length(.) > 0">
			<reference typeCode="REFR">
				<document classCode="DOC" moodCode="EVN">
				<code code="{$documentsHeldBySender}" codeSystem="{$oidichreferencesource}" displayName="documentsHeldBySender"/>
					<title><xsl:value-of select="."/></title>
				</document>
			</reference>
		</xsl:if>
	</xsl:template>
	
	<!-- Fulfil Expedited Criteria: 
	E2B(R2): element "documentlist" inside "safetyreport"
	E2B(R3): element "component"
	-->
	<xsl:template name="fulfillexpeditecriteria">
		<!-- A.1.9 - Does this Case Fulfil the Local Criteria for an Expedited Report? -->
		<component typeCode="COMP">
			<observationEvent classCode="OBS" moodCode="EVN">
				<code code="{$LocalCriteriaForExpedited}" codeSystem="{$oidObservationCode}"/>
				<xsl:choose>
					<xsl:when test="fulfillexpeditecriteria = 1">
						<value xsi:type="BL" value="true"/>
					</xsl:when>
					<xsl:when test="fulfillexpeditecriteria = 2">
						<value xsi:type="BL" value="false"/>
					</xsl:when>
					<xsl:otherwise>
						<value xsi:type="BL" nullFlavor="NI"/>
					</xsl:otherwise>
				</xsl:choose>
			</observationEvent>
		</component>
	</xsl:template>
	
	<!-- Linked Report: 
	E2B(R2): element "linkedreport" inside "safetyreport"
	E2B(R3): element "relatedInvestigation"
	-->
	<xsl:template match="linkedreport">
		<!-- A.1.12.r Identification Number of the Report Which Is Linked to this Report -->
		<xsl:if test="string-length(linkreportnumb)>0">
			<outboundRelationship typeCode="SPRT">
				<relatedInvestigation classCode="INVSTG" moodCode="EVN">
					<code nullFlavor="NA"/>
					<subjectOf2 typeCode="SUBJ">
						<controlActEvent classCode="CACT" moodCode="EVN">
							<id extension="{linkreportnumb}" root="{$oidWorldWideCaseID}"/>
						</controlActEvent>
					</subjectOf2>
				</relatedInvestigation>
			</outboundRelationship>
		</xsl:if>
	</xsl:template>
	
	<!-- Report Duplicate : 
	E2B(R2): element "reportduplicate" inside "safetyreport"
	E2B(R3): element "controlActEvent"
	-->
	<xsl:template match="reportduplicate">
		<xsl:if test="string-length(duplicatesource)>0 or string-length(duplicatenumb)>0">
			<subjectOf1 typeCode="SUBJ">
				<controlActEvent classCode="CACT" moodCode="EVN">
					<!-- A.1.11.r.1 Source(s) of the Case Identifier -->
					<!-- A.1.11.r.2 Case Identifier(s) -->
					<xsl:choose>
						<xsl:when test="string-length(duplicatesource) = 0"><id assigningAuthorityName="-" extension="{duplicatenumb}" root="{$oidCaseIdentifier}"/></xsl:when>
						<xsl:when test="string-length(duplicatenumb) = 0"><id assigningAuthorityName="{duplicatesource}" extension="-" root="{$oidCaseIdentifier}"/></xsl:when>
						<xsl:otherwise><id assigningAuthorityName="{duplicatesource}" extension="{duplicatenumb}" root="{$oidCaseIdentifier}"/></xsl:otherwise>
					</xsl:choose>
				</controlActEvent>
			</subjectOf1>
		</xsl:if>
	</xsl:template>
	
</xsl:stylesheet>
