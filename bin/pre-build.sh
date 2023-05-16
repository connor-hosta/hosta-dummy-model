# Get the image details with the specified tag
image_details=$(aws ecr describe-images --repository-name $MODEL_NAME --filter "tagStatus=TAGGED" --query "imageDetails[?contains(imageTags, PROJECT_VERSION)]" --output json)

# Check if image_details is not empty
if [[ "$image_details" != "[]" ]]; then
  # Extract the image digest of the first image in the list
  image_digest=$(echo "$image_details" | jq -r '.[0].imageDigest')

  # Update the tag of the image to "latest"
  aws ecr put-image --repository-name $MODEL_NAME --image-digest "$image_digest" --image-tag latest

  # terminate build
  aws codebuild stop-build --id ${CODEBUILD_BUILD_ID}
fi
