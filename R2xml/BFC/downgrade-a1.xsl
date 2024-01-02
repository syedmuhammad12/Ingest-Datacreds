<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - Backbone & A.1 Part)
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

		Version:		1.1
		Date:			05/07/2016
		Status:			Final
		Author:			Nick Halsey (EU)
		Amendment:	Bug fix for seriousness flags 

		Version:		1.2
		Date:			05/07/2017
		Status:			Final
		Author:			Nick Halsey (EU)
		Amendment:	Bug fix for A.1.11 Other case identifiers in previous transmissions, fix seriousness flags for boolean false	value
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!-- A.1. Case Safety Report (level of investigationEvent)-->
	<xsl:template name="safetyreportheader">
		<!-- A.1.0.1 Sender’s Case Safety Report Unique Identifier -->
		<safetyreportid><xsl:value-of select="hl7:id[@root=$oidSendersReportNamespace]/@extension"/></safetyreportid>
		<!-- A.1.1 = A.2.r.1.3 of the first Primary Source where A.2.r.1.5 = 1 - Rule STR-01 -->
		<xsl:apply-templates select="hl7:outboundRelationship[hl7:priorityNumber/@value='1']/hl7:relatedInvestigation[hl7:code/@code=$SourceReport and hl7:code/@codeSystem=$oidReportRelationCode]" mode="ps-country"/>
		<!-- A.1.2. = first existing B.2.i.8 - Rule STR-02 -->
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2[hl7:observation/hl7:code/@code=$Reaction][1]" mode="occur-country"/>
		<!-- A.1.3 Date of this transmission -->
		<xsl:call-template name="convertDate">
			<xsl:with-param name="elementName">transmissiondate</xsl:with-param>
			<xsl:with-param name="date-value" select="../../hl7:effectiveTime/@value"/>
			<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
			<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
		</xsl:call-template>
		<!-- A.1.4 Type of report -->
		<reporttype><xsl:value-of select="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$ReportType]/hl7:value[@xsi:type='CE' and @codeSystem=$oidReportType]/@code"/></reporttype>
		<!-- A.1.5. Seriousness-->
		<xsl:call-template name="Seriousness"/>
		<!-- A.1.6 Date Report Was First Received from Source -->
		<xsl:call-template name="convertDate">
			<xsl:with-param name="elementName">receivedate</xsl:with-param>
			<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
			<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
			<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
		</xsl:call-template>
		<!-- A.1.7 Date of Most Recent Information for this Case -->
		<xsl:call-template name="convertDate">
			<xsl:with-param name="elementName">receiptdate</xsl:with-param>
			<xsl:with-param name="date-value" select="hl7:availabilityTime/@value"/>
			<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
			<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
		</xsl:call-template>
		<!-- A.1.8 Additional documents -->
		<additionaldocument>1</additionaldocument>
		<!-- A.1.8.1.r.1 DocumentList -->
		<xsl:call-template name="DocumentList">
			<xsl:with-param name="Length">100</xsl:with-param>
		</xsl:call-template>
		<!-- A.1.9 Does this Case Fulfill the Local Criteria for an Expedited Report? -->
		<xsl:if test="hl7:component/hl7:observationEvent[hl7:code/@code=$LocalCriteriaForExpedited and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value">
			<fulfillexpeditecriteria>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type">YESNO</xsl:with-param>
					<xsl:with-param name="code" select="hl7:component/hl7:observationEvent[hl7:code/@code=$LocalCriteriaForExpedited and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
				</xsl:call-template>
			</fulfillexpeditecriteria>
		</xsl:if>
		<!-- A.1.10 Worldwide unique case identification number-->
		<xsl:choose>
			<xsl:when test="hl7:outboundRelationship/hl7:relatedInvestigation[hl7:code/@code=$InitialReport and hl7:code/@codeSystem=$oidReportRelationCode]/hl7:subjectOf2/hl7:controlActEvent/hl7:author/hl7:assignedEntity/hl7:code/@code=1">
				<authoritynumb>
					<xsl:value-of select="hl7:id[@root=$oidWorldWideCaseID]/@extension"/>
				</authoritynumb>
			</xsl:when>
			<xsl:otherwise>
				<companynumb>
					<xsl:value-of select="hl7:id[@root=$oidWorldWideCaseID]/@extension"/>
				</companynumb>
			</xsl:otherwise>
		</xsl:choose>
		<!-- A.1.11 Other case identifiers in previous transmissions-->
		<xsl:if test="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$OtherCaseIDs and hl7:code/@codeSystem=$oidReportCharacterizationCode]/hl7:value/@value ='true'">
			<duplicate>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type">YESNO</xsl:with-param>
					<xsl:with-param name="code" select="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$OtherCaseIDs and hl7:code/@codeSystem=$oidReportCharacterizationCode]/hl7:value/@value"/>
				</xsl:call-template>
				
			</duplicate>
		</xsl:if>
		<!-- A.1.13 Report nullification -->
		<xsl:if test="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$NullificationAmendmentCode and hl7:code/@codeSystem=$oidReportCharacterizationCode]/hl7:value/@code=1">
			<casenullification>1</casenullification>
			<nullificationreason>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string"><xsl:value-of select="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$NullificationAmendmentReason and hl7:code/@codeSystem=$oidReportCharacterizationCode]/hl7:value/hl7:originalText"/></xsl:with-param>
					<xsl:with-param name="string-length">200</xsl:with-param>
				</xsl:call-template>
			</nullificationreason>
		</xsl:if>
		<!-- repeatable elements -->
		<!-- A.1.11.r.2 Identification of duplicate reports -->
		<xsl:call-template name="ReportDuplicate">
			<xsl:with-param name="Length">50</xsl:with-param>
		</xsl:call-template>
		<!-- A.1.12.r Identification number of the report which is linked to this report -->
		<xsl:apply-templates select="hl7:outboundRelationship/hl7:relatedInvestigation/hl7:subjectOf2/hl7:controlActEvent/hl7:id" mode="LinkedReport"/>
	</xsl:template>
	
	<!-- A.1.1 Primary source country - Rule STR-01 -->
	<xsl:template match="hl7:relatedInvestigation" mode="ps-country">
		<primarysourcecountry>
			<xsl:value-of select="hl7:subjectOf2/hl7:controlActEvent/hl7:author/hl7:assignedEntity/hl7:assignedPerson/hl7:asLocatedEntity/hl7:location/hl7:code/@code"/>
		</primarysourcecountry>
	</xsl:template>
	
	<!-- A.1.2 Occur country - Rule STR-02 -->
	<xsl:template match="hl7:subjectOf2" mode="occur-country">
		<occurcountry>
			<xsl:value-of select="hl7:observation/hl7:location/hl7:locatedEntity/hl7:locatedPlace/hl7:code/@code"/>
		</occurcountry>
	</xsl:template>
	
	<!-- A.1.5. Seriousness = all the seriousness criteria set for any event B.2.i.2 fields -->
	<xsl:template name="Seriousness">
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="serious">
			<xsl:with-param name="elementName">serious</xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnessdeath</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$ResultsInDeath"/></xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnesslifethreatening</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$LifeThreatening" /></xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnesshospitalization</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$CausedProlongedHospitalisation" /></xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnessdisabling</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$DisablingIncapaciting" /></xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnesscongenitalanomali</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$CongenitalAnomalyBirthDefect" /></xsl:with-param>
		</xsl:apply-templates>
		<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="seriousness">
			<xsl:with-param name="elementName">seriousnessother</xsl:with-param>
			<xsl:with-param name="observationCode"><xsl:value-of select="$OtherMedicallyImportantCondition" /></xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	
	<!-- A.1.5 - serious if any seriousness criteria in any serious event-->
	<xsl:template match="hl7:primaryRole" mode="serious">
		<xsl:param name="elementName"/>
		<xsl:variable name="allSeriousness" 
			select="count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$ResultsInDeath and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true']) + count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$LifeThreatening and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true']) + count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CausedProlongedHospitalisation and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true']) + count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$DisablingIncapaciting and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true']) + count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CongenitalAnomalyBirthDefect and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true']) + count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$OtherMedicallyImportantCondition and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true'])"/>
			
			<!--  and hl7:code/@codeSystem=$oidObservationCode -->
		<xsl:element name="{$elementName}">
			<xsl:choose>
				<xsl:when test="$allSeriousness > 0"><xsl:text>1</xsl:text></xsl:when>		<!-- serious -->
				<xsl:when test="$allSeriousness = 0"><xsl:text>2</xsl:text></xsl:when>		<!-- not serious -->
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	
	<!-- service that transforms any seriousness from R3 to R2 -->
	<xsl:template match="hl7:primaryRole" mode="seriousness">
		<xsl:param name="elementName"/>
		<xsl:param name="observationCode"/>
		<xsl:element name="{$elementName}">
			<xsl:choose>
				<xsl:when test="count(hl7:subjectOf2/hl7:observation/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$observationCode and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@value='true'])> 0">
					<xsl:text>1</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:text>2</xsl:text>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	
	<!-- A.1.8.1.r.1 - DocumentList = concat all documents with seperator-->
	<xsl:template name="DocumentList">
		<xsl:param name="NarrativeText"/>
		<xsl:param name="Length">0</xsl:param>
		<xsl:variable name="ContentString">Source of this Case Safety Report in E2B(R3) Format: Additional documents: <xsl:for-each select="hl7:reference/hl7:document/hl7:title"><xsl:text>; </xsl:text><xsl:value-of select="."/></xsl:for-each></xsl:variable>
		<xsl:choose>
			<xsl:when test="$NarrativeText=''">
				<xsl:if test="string-length($ContentString) > 0">
					<documentlist>
						<xsl:call-template name="truncate">
							<xsl:with-param name="string"><xsl:value-of select="$ContentString"/></xsl:with-param>
							<xsl:with-param name="string-length"><xsl:value-of select="$Length" /></xsl:with-param>
						</xsl:call-template>
					</documentlist>
				</xsl:if>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="string-length($ContentString)>$Length">
					<xsl:value-of select="$NarrativeText" />
					<xsl:value-of select="$ContentString" />
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- A.1.11.r.1 - A.1.11.r.2 Other case identifiers in previous transmissions-->
	<xsl:template name="ReportDuplicate">
		<xsl:param name="NarrativeText"/>
		<xsl:param name="Length">0</xsl:param>
		<xsl:for-each select="hl7:subjectOf1/hl7:controlActEvent/hl7:id">
			<xsl:choose>
				<xsl:when test="$NarrativeText=''">
					<reportduplicate>
						<duplicatesource>
							<xsl:call-template name="truncate">
								<xsl:with-param name="string"><xsl:value-of select="@assigningAuthorityName"/></xsl:with-param>
								<xsl:with-param name="string-length"><xsl:value-of select="$Length" /></xsl:with-param>
							</xsl:call-template>
						</duplicatesource>
						<duplicatenumb>
							<xsl:value-of select="@extension"/>
						</duplicatenumb>
					</reportduplicate>
				</xsl:when>
				<xsl:otherwise>
					<xsl:if test="string-length(@assigningAuthorityName)>$Length">
						<xsl:value-of select="$NarrativeText" />
						<xsl:value-of select="@extension" /> : <xsl:value-of select="@assigningAuthorityName" />
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>
	
	<!-- A.1.12.r Identification number of the report which is linked to this report -->
	<xsl:template match="hl7:id" mode="LinkedReport">
		<xsl:if test="string-length(@extension)>0">
			<linkedreport>
				<linkreportnumb>
					<xsl:value-of select="@extension"/>
				</linkreportnumb>
			</linkedreport>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
