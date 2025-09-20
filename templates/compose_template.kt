package {package_name}

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

val {IconName}: ImageVector
    get() {
        if (_{iconName} != null) {
            return _{iconName}!!
        }
        _{iconName} = ImageVector.Builder(
            name = "{IconName}",
            defaultWidth = {width}.dp,
            defaultHeight = {height}.dp,
            viewportWidth = {viewportWidth}f,
            viewportHeight = {viewportHeight}f
        ).apply {
            {path_definitions}
        }.build()
        return _{iconName}!!
    }

private var _{iconName}: ImageVector? = null